import dash
from dash import dcc, html, Output, Input
from dash.dash_table import DataTable
import plotly.graph_objs as go
import subprocess
import threading
import time
import psutil

# Global storage
gpu_info = []
gpu_data_log = {}
system_data_log = []
monitoring_active = True

# Detect GPUs
def detect_gpus():
    """
    Detects available GPUs using nvidia-smi, populates gpu_info with name and
    their maximum power limit (TDP), and initializes gpu_data_log.
    """
    global gpu_info, gpu_data_log

    # Get GPU names
    name_result = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True)
    name_lines = name_result.stdout.strip().split('\n')
    
    # Get GPU maximum power limits
    # This query retrieves the hardware enforced power limit for each GPU.
    power_limit_cmd = ["nvidia-smi", "--query-gpu=power.max_limit", "--format=csv,noheader,nounits"]
    power_limit_result = subprocess.run(power_limit_cmd, capture_output=True, text=True)
    power_limit_lines = power_limit_result.stdout.strip().split('\n')

    gpu_info = []
    for i, name_line in enumerate(name_lines):
        gpu_name = name_line.split(":")[1].split("(")[0].strip()
        max_power_limit = None
        
        # Parse max power limit, handling potential errors or missing values
        if i < len(power_limit_lines) and power_limit_lines[i].strip():
            try:
                max_power_limit = float(power_limit_lines[i].strip())
            except ValueError:
                # If parsing fails, set a default or warn
                print(f"Warning: Could not parse max power limit for GPU {i}: '{power_limit_lines[i].strip()}'. Setting to 0.")
                max_power_limit = 0.0 # Fallback to 0.0 if value is unparseable
        
        gpu_info.append({"id": i, "name": gpu_name, "power_max_limit": max_power_limit})
    
    # Initialize data log for each GPU
    gpu_data_log = {gpu["id"]: [] for gpu in gpu_info}

# GPU Monitoring
def monitor_gpus():
    """
    Continuously monitors GPU performance metrics (current power draw, memory used,
    temperature, GPU utilization, memory utilization) using nvidia-smi
    and stores the data in gpu_data_log.
    """
    global gpu_data_log
    # Query for relevant GPU metrics
    cmd = ["nvidia-smi", "--query-gpu=timestamp,power.draw,memory.used,temperature.gpu,utilization.gpu,utilization.memory",
           "--format=csv,noheader,nounits", "-l", "1"] # -l 1 updates every second
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

    while monitoring_active:
        # Read a batch of lines corresponding to the number of GPUs detected
        batch_lines = [process.stdout.readline().strip() for _ in range(len(gpu_info))]
        for i, line in enumerate(batch_lines):
            values = line.split(", ")
            entry = {
                "timestamp": values[0],
                "power": float(values[1]),        # Current power draw in Watts
                "memory": float(values[2]),       # Memory used in MB
                "temperature": float(values[3]),  # GPU temperature in Celsius
                "gpu_util": float(values[4]),     # GPU utilization percentage
                "mem_util": float(values[5])      # Memory utilization percentage
            }
            gpu_data_log[i].append(entry)
            if len(gpu_data_log[i]) > 15:  # Keep only last 15 entries for a concise rolling window
                gpu_data_log[i].pop(0)
        time.sleep(0.1) # Small delay to prevent busy-waiting and allow other threads to run

# System Monitoring
def monitor_system():
    """
    Continuously monitors CPU and RAM utilization of the system
    and stores the data in system_data_log.
    """
    global system_data_log
    while monitoring_active:
        entry = {
            "timestamp": time.strftime("%H:%M:%S"), # Current time
            "cpu_util": psutil.cpu_percent(),       # CPU utilization percentage
            "ram_util": psutil.virtual_memory().percent, # RAM utilization percentage
        }
        system_data_log.append(entry)
        if len(system_data_log) > 15: # Keep only last 15 entries
            system_data_log.pop(0)
        time.sleep(1) # Monitor every second

# Dash App Setup
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Real-Time GPU & System Performance Monitor", style={"textAlign": "center", "color": "#2C3E50", "padding": "20px"}),
    dcc.Interval(id="interval-component", interval=1000, n_intervals=0), # Interval for updating graphs every 1000ms (1 second)
    html.Div(id="gpu-graphs-container"), # Container for dynamically generated GPU graphs and tables
    html.Div([
        html.H2("CPU Utilization", style={"textAlign": "center", "color": "#2C3E50", "marginTop": "30px"}),
        dcc.Graph(id="cpu-graph")
    ], style={"width": "90%", "margin": "auto", "padding": "20px", "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)", "borderRadius": "10px", "backgroundColor": "#FDFEFE"}),
    html.Div([
        html.H2("RAM Utilization", style={"textAlign": "center", "color": "#2C3E50", "marginTop": "30px"}),
        dcc.Graph(id="ram-graph")
    ], style={"width": "90%", "margin": "auto", "padding": "20px", "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)", "borderRadius": "10px", "backgroundColor": "#FDFEFE", "marginBottom": "50px"})
], style={"fontFamily": "Arial, sans-serif", "backgroundColor": "#ECF0F1"})

# Helper function to get emoji based on temperature for a fun visual status
def get_temp_emoji(temp_c):
    """
    Returns a funny emoji based on the temperature in Celsius.
    Ranges are defined to provide a clear and amusing visual status.
    """
    if temp_c >= 100:
        return "💀" # Dead face for extreme temperatures
    elif temp_c >= 90:
        return "🔥" # Fire for very hot
    elif temp_c >= 80:
        return "🥵" # Overheated/stressed face
    elif temp_c >= 75:
        return "😩" # Exhausted/stressed
    elif temp_c >= 70:
        return "😟" # Worried face
    elif temp_c >= 60:
        return "😅" # Sweating a bit
    elif temp_c >= 50:
        return "🙂" # Smiling face for good temperature
    elif temp_c >= 40:
        return "😊" # Happy face
    elif temp_c >= 30:
        return "🥶" # Freezing face
    elif temp_c >= 20:
        return "🆒" # Cool
    else:
        return "🧊" # Ice cold

# GPU Table
def create_gpu_table(gpu_id):
    """
    Generate a formatted DataTable for the last 15 GPU records.
    Includes the new 'Temp Status' column with emojis.
    Colors for GPU utilization, memory utilization, power, and temperature are applied
    via style_data_conditional to match graph colors.
    """
    data_raw = gpu_data_log.get(gpu_id, [])[-15:] # Get last 15 entries for the specified GPU
    
    # Add 'temp_status' field to each data entry for the emoji column
    data_with_emoji = []
    for entry in data_raw:
        new_entry = entry.copy()
        new_entry["temp_status"] = get_temp_emoji(entry["temperature"])
        data_with_emoji.append(new_entry)

    return DataTable(
        columns=[
            {"name": "Time", "id": "timestamp"},
            {"name": "Power (W)", "id": "power"},
            {"name": "Memory (MB)", "id": "memory"},
            {"name": "Temp (°C)", "id": "temperature"},
            {"name": "Temp Status", "id": "temp_status"}, # New column for emoji status
            {"name": "GPU Util (%)", "id": "gpu_util"},
            {"name": "Mem Util (%)", "id": "mem_util"},
        ],
        data=data_with_emoji,
        style_table={"width": "100%", "overflowX": "auto", "marginTop": "20px"},
        style_header={"backgroundColor": "#34495E", "color": "white", "fontWeight": "bold", "textAlign": "center"},
        style_data_conditional=[
            # Styling for GPU Util column (GREEN text)
            {"if": {"column_id": "gpu_util"}, "color": "green"},
            # Styling for Mem Util column (BLUE text)
            {"if": {"column_id": "mem_util"}, "color": "blue"},
            # Styling for Power (W) column (YELLOW text, using darkgoldenrod for contrast)
            {"if": {"column_id": "power"}, "color": "darkgoldenrod"}, 
            # Styling for Temp (°C) column (RED text)
            {"if": {"column_id": "temperature"}, "color": "red"},

            # Conditional background for high GPU utilization (light red)
            {"if": {"column_id": "gpu_util", "filter_query": "{gpu_util} > 90"}, "backgroundColor": "rgba(255, 99, 71, 0.3)"}, 
            # Conditional background for high temperature (light orange)
            {"if": {"column_id": "temperature", "filter_query": "{temperature} > 80"}, "backgroundColor": "rgba(255, 160, 0, 0.3)"}, 
        ],
        editable=False,
        cell_selectable=False,
        style_cell={"textAlign": "center", "minWidth": "100px", "padding": "8px"},
        style_as_list_view=True, # Makes the table look more like a simple list
    )

# GPU Graphs Container
@app.callback(
    Output("gpu-graphs-container", "children"),
    Input("interval-component", "n_intervals")
)
def update_gpu_graphs_container(n):
    """
    Dynamically updates the container with individual GPU graphs and tables
    for each detected GPU. This function runs periodically to refresh the layout.
    """
    children = []
    for gpu in gpu_info:
        gpu_id = gpu["id"]
        children.append(html.Div([
            html.H2(f"GPU {gpu_id} - {gpu['name']}", style={"textAlign": "center", "color": "#2C3E50"}),
            dcc.Graph(id={"type": "gpu-graph", "index": gpu_id}), # Graph component for this GPU
            create_gpu_table(gpu_id) # Table component for this GPU
        ], style={"width": "90%", "margin": "auto", "padding": "20px", "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)", "borderRadius": "10px", "backgroundColor": "#FDFEFE", "marginBottom": "30px"}))
    return children

# GPU Graphs Update
@app.callback(
    Output({'type': 'gpu-graph', 'index': dash.MATCH}, 'figure'), # Targets a specific GPU graph by its ID
    Input("interval-component", "n_intervals"),
    dash.State({'type': 'gpu-graph', 'index': dash.MATCH}, 'id') # Retrieves the ID of the specific graph being updated
)
def update_gpu_graph(n, id):
    """
    Updates the specific GPU graph with real-time data for GPU Util, Mem Util,
    Power (scaled to percentage of max TDP), and Temperature.
    Uses specified colors for each line.
    """
    gpu_id = id["index"]
    data = gpu_data_log.get(gpu_id, [])
    x = [entry["timestamp"].split(" ")[1] for entry in data] # Extracting time part for x-axis labels
    
    y_gpu_util = [entry["gpu_util"] for entry in data]
    y_mem_util = [entry["mem_util"] for entry in data]
    y_temp = [entry["temperature"] for entry in data]

    # Find the max power limit for the current GPU
    gpu_max_power_limit = 0.0 # Default to 0.0 to prevent division by zero
    for gpu_item in gpu_info:
        if gpu_item["id"] == gpu_id:
            if gpu_item["power_max_limit"] is not None and gpu_item["power_max_limit"] > 0:
                gpu_max_power_limit = gpu_item["power_max_limit"]
            break

    # Calculate power as a percentage of max power limit (TDP)
    y_power_percent = []
    if gpu_max_power_limit > 0:
        y_power_percent = [(entry["power"] / gpu_max_power_limit) * 100 for entry in data]
    else:
        # If max power limit is not available or 0, display power as 0%
        y_power_percent = [0.0] * len(data)

    fig = go.Figure()
    
    # GPU Utilization - Green line
    fig.add_trace(go.Scatter(x=x, y=y_gpu_util, mode="lines+markers", name="GPU Util (%)", line=dict(color="green")))
    # Memory Utilization - Blue line
    fig.add_trace(go.Scatter(x=x, y=y_mem_util, mode="lines+markers", name="Mem Util (%)", line=dict(color="blue")))
    # Power Utilization - Yellow line (scaled to percentage of max TDP)
    fig.add_trace(go.Scatter(x=x, y=y_power_percent, mode="lines+markers", name="Power Util (%)", line=dict(color="darkgoldenrod"))) # Darker yellow for better visibility
    # Temperature - Red line
    fig.add_trace(go.Scatter(x=x, y=y_temp, mode="lines+markers", name="Temp (°C)", line=dict(color="red")))

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Value (%) / Temp (°C)", # Updated y-axis title to reflect mixed units
        yaxis=dict(range=[0, 100]), # Keep y-axis range from 0 to 100 for consistent scaling
        legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1), # Legend positioning
        hovermode="x unified", # Shows all trace values at a given x-point on hover
        margin=dict(l=40, r=40, t=40, b=40), # Graph margins
        plot_bgcolor="#FDFEFE", # Plot background color
        paper_bgcolor="#FDFEFE" # Paper (overall graph) background color
    )
    
    return fig

# CPU Graph Update
@app.callback(Output("cpu-graph", "figure"), Input("interval-component", "n_intervals"))
def update_cpu_graph(n):
    """
    Updates the CPU utilization graph.
    """
    x = [entry["timestamp"] for entry in system_data_log]
    y = [entry["cpu_util"] for entry in system_data_log]
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode="lines+markers", name="CPU Util", line=dict(color="purple")))
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="CPU (%)",
        yaxis=dict(range=[0, 100]),
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor="#FDFEFE",
        paper_bgcolor="#FDFEFE"
    )
    return fig

# RAM Graph Update
@app.callback(Output("ram-graph", "figure"), Input("interval-component", "n_intervals"))
def update_ram_graph(n):
    """
    Updates the RAM utilization graph.
    """
    x = [entry["timestamp"] for entry in system_data_log]
    y = [entry["ram_util"] for entry in system_data_log]
    fig = go.Figure(data=go.Scatter(x=x, y=y, mode="lines+markers", name="RAM Util", line=dict(color="orange")))
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="RAM (%)",
        yaxis=dict(range=[0, 100]),
        margin=dict(l=40, r=40, t=40, b=40),
        plot_bgcolor="#FDFEFE",
        paper_bgcolor="#FDFEFE"
    )
    return fig

# Background Threads for continuous monitoring
if __name__ == '__main__':
    detect_gpus() # Detect GPUs and their max power limits once at startup
    # Start monitoring threads as daemon threads so they terminate automatically with the main program
    threading.Thread(target=monitor_gpus, daemon=True).start()
    threading.Thread(target=monitor_system, daemon=True).start()
    # Run the Dash application in debug mode for development, accessible locally
    app.run(debug=True, host="127.0.0.1", port=5000)

