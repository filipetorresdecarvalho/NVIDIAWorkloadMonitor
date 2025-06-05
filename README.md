# **🚀 NVIDIA Workload Monitor (NWM): The Ultimate Performance & Health Dashboard for NVIDIA GPUs**

## **Welcome to Unprecedented System Insight\! 👋**

Are you tired of juggling between basic system monitors like Windows Task Manager and the raw, often overwhelming output of nvidia-smi commands? The **NVIDIA Workload Monitor (NWM)** is here to revolutionize how you understand and manage your NVIDIA GPU and system performance. This application provides a sophisticated, real-time graphical interface, presenting critical data in an intuitive dashboard, complete with interactive graphs and easily digestible spreadsheets (data tables).

Unlike traditional tools, NWM is designed to give you **more than just numbers**; it offers a visual narrative of your system's behavior. While Task Manager provides only superficial GPU utilization, and nvidia-smi gives you detailed but static command-line snapshots, NWM transforms this information into a dynamic, user-friendly experience. Soon, it will also automatically download comprehensive **logs in both CSV and JSON formats every minute**, offering an invaluable historical record of your system's performance. This level of automated data collection and presentation goes far beyond what built-in tools or simple command-line outputs can provide.

### **Why NWM is Your Next Essential Tool:**

For professionals in **3D rendering, AI/Machine Learning, and scientific computing**, understanding your hardware's behavior under extreme load is paramount. This is where NWM truly shines:

* **Beyond Basic Monitoring:** While it's useful for any NVIDIA GPU user, NWM's depth of information is especially critical for **multi-GPU setups** common in data centers and high-performance workstations. It provides detailed, per-GPU metrics that are essential for balancing workloads, identifying bottlenecks, and optimizing complex applications.  
* **Diagnosing the "Why":** Crashes, slowdowns, or unexpected power consumption in AI training or 3D rendering are often mysteries with generic monitors. NWM provides the granular temperature, power draw, and utilization data needed to precisely understand *why* an application behaved a certain way, leading to faster debugging and more stable operations.  
* **Aimed at Professionals, Not Just Gamers:** While NWM can certainly be used to monitor your GPU during gaming sessions, its core focus is not on gaming-specific metrics like FPS (Frames Per Second). Instead, it prioritizes the deep system and GPU health data that **3D and AI professionals** desperately need. Gaming has its own suite of specialized tools; AI and demanding 3D workflows often lack comprehensive, easy-to-interpret monitoring solutions, especially for datacenter GPUs where continually running shell prompts like MSDOS is cumbersome and time-consuming.  
* **More Than nvidia-smi:** Beyond presenting nvidia-smi data graphically, NWM encompasses broader system metrics (CPU, RAM) and is designed to evolve with additional features that go beyond the scope of a single command-line utility.

## **✨ Features (Current Version)**

This is the **first version** of NVIDIA Workload Monitor, laying a robust foundation for future enhancements. Currently, NWM provides:

* **Dynamic GPU Insights:** Visualizes crucial metrics for each detected NVIDIA GPU:  
  * **GPU Utilization (%):** How busy your GPU's processing units are.  
  * **Memory Utilization (%):** Percentage of your GPU's dedicated memory in use.  
  * **Power Draw (W):** Real-time power consumption, scaled as a percentage of your GPU's maximum power limit (TDP).  
  * **Temperature (°C):** Current GPU core temperature, with fun emoji indicators for quick visual status.  
* **System-Wide Performance:** Monitors your CPU and RAM utilization:  
  * **CPU Utilization (%):** Overall processor activity.  
  * **RAM Utilization (%):** System memory usage.  
* **Interactive Graphs:** Utilizes Plotly to provide engaging, real-time line graphs for all metrics, allowing you to easily track trends over time.  
* **Detailed Data Tables:** Presents the last 15 data entries for each GPU in clear, color-coded tables, making it easy to spot anomalies.  
* **Cross-Platform Compatibility:** Designed to work on any system (Linux/Windows) with NVIDIA GPUs and installed drivers.

## **🚀 Future Vision & Ideas**

NWM is just getting started\! We have a lot of exciting ideas planned to expand its capabilities and make it an even more powerful tool:

* **Automated Log Downloads:** Implementing the automatic CSV and JSON log downloads every minute for comprehensive historical analysis.  
* **Process-Level GPU Monitoring:** Identifying and displaying which specific processes are using your GPUs and how much.  
* **Advanced Alerting:** Notifying users of critical events like thermal throttling, power limit exceedances, or unusual resource spikes.  
* **Historical Data Analysis:** Features for reviewing and comparing performance logs over longer periods.  
* **Customizable Dashboards:** Allowing users to tailor the displayed metrics and layout to their specific needs.  
* **Remote Monitoring:** Exploring options for monitoring systems over a network.

## **🏁 Getting Started**

To get the NVIDIA Workload Monitor up and running on your local machine, please follow these steps carefully.

**⚠️ IMPORTANT: NVIDIA-SMI Requirement ⚠️**

This application relies heavily on the nvidia-smi command-line utility. This means you must have an **NVIDIA GPU** and **NVIDIA drivers** installed on your system for the GPU monitoring features to function correctly.

**⚠️ IMPORTANT: Download the Entire Project Folder\! ⚠️**

This application requires multiple files and folders (app.py, setup.py, requirements.txt). **Please do NOT attempt to download individual files (e.g., just app.py or setup.py)** as the application will not function correctly without all its components.

### **Option 1: Clone the Repository (Recommended)**

The best way to get started is by cloning the Git repository. This ensures you have the complete project structure and makes future updates easier.

1. **Open your terminal or Git Bash.**  
2. **Navigate to the directory** where you want to save the project:  
   cd /path/to/your/desired/directory

3. **Clone the repository:**  
   git clone https://github.com/filipetorresdecarvalho/NVIDIAWorkloadMonitor.git

4. **Navigate into the cloned project directory:**  
   cd NVIDIAWorkloadMonitor

### **Option 2: Download the Project as a ZIP**

If you prefer not to use Git, you can download the entire project as a ZIP archive.

1. Go to the GitHub repository page: [https://github.com/filipetorresdecarvalho/NVIDIAWorkloadMonitor](https://github.com/filipetorresdecarvalho/NVIDIAWorkloadMonitor)  
2. Click the green **"Code"** button.  
3. Select **"Download ZIP"**.  
4. Extract the downloaded ZIP file to your desired location.

### **⚙️ First Run Setup**

**Before you run the application for the first time, you MUST execute the setup.py script.** This script will automatically download the latest requirements.txt from GitHub and install all necessary Python dependencies.

1. **Open your terminal or command prompt.**  
2. **Navigate into the NVIDIAWorkloadMonitor project directory** (if you're not already there):  
   cd /path/to/NVIDIAWorkloadMonitor

3. **Run the setup script:**  
   python setup.py

   This process may take a few moments as it installs packages. Please ensure you have an active internet connection.

### **▶️ Running the Application**

Once setup.py has completed successfully, you can launch the Dash application:

1. From the NVIDIAWorkloadMonitor directory in your terminal, run:  
   python app.py

2. The application will start, and you'll see a message like Dash is running on http://127.0.0.1:8050/.  
3. Open your web browser and go to the address provided (usually http://127.0.0.1:8050/) to access your real-time NVIDIA Workload Monitor\!

## **🤝 Contributing & Suggestions**

We are always open to suggestions, ideas, and contributions\! If you have thoughts on how to improve the NVIDIA Workload Monitor, new features you'd like to see, or encounter any issues, please feel free to:

* Open an issue on the [GitHub Issues page](https://github.com/filipetorresdecarvalho/NVIDIAWorkloadMonitor/issues)  
* Fork the repository and submit a pull request with your changes.

Your feedback is invaluable in shaping the future of this project\!

## **🙏 Support My Work**

If you find the NVIDIA Workload Monitor useful and would like to support its continued development and future enhancements, any donation would be greatly appreciated. Your generosity helps keep this project alive and evolving.

You can send donations to the following Bitcoin address:

4AtJCocHeeQ4kbJZLwUhy6Gm5cM45T19eVsAHfom3eY2YyNx1qcWPnQNkAnpWGdnxuLw1avuqMthj5sGRGz7vVbPEFRqaLT

Thank you for considering\!

## **❤️ A Special Thank You\!**

Thank you for checking out the NVIDIA Workload Monitor\! I hope it becomes an indispensable tool for your 3D rendering, AI development, and system optimization endeavors.

## **📄 License**

This project is licensed under the MIT License \- see the [LICENSE](http://docs.google.com/LICENSE) file for details.