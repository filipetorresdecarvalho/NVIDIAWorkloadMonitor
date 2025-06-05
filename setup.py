import subprocess
import sys
import os
import requests
import shutil # For cleaning up temporary files

# Define your GitHub repository URL and branch for the GPU Monitor App
# IMPORTANT: Update this URL to your actual GitHub repository for this project!
GITHUB_REPO_URL = "https://github.com/filipetorresdecarvalho/GPUMonitorApp"
GITHUB_BRANCH = "main" # Assuming 'main' is your default branch

# Define the local path for the downloaded requirements file
TEMP_REQUIREMENTS_FILE = "temp_requirements.txt"

def run_command(command, message):
    """Executes a shell command and provides feedback."""
    print(f"\n--- {message} ---")
    try:
        result = subprocess.run(
            command,
            check=True,
            shell=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"Errors/Warnings:\n{result.stderr}")
        print(f"--- {message} complete ---")
    except subprocess.CalledProcessError as e:
        print(f"Error during '{command}':")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Command '{command.split()[0]}' not found.")
        print("Please ensure Python and pip are installed and in your PATH.")
        sys.exit(1)

def download_file_from_github(repo_url, branch, file_path_in_repo, local_save_path):
    """
    Downloads a specific file from a GitHub repository.
    Args:
        repo_url (str): The base URL of the GitHub repository (e.g., "https://github.com/user/repo").
        branch (str): The branch name (e.g., "main").
        file_path_in_repo (str): The path to the file within the repository (e.g., "requirements.txt").
        local_save_path (str): The local path where the file should be saved.
    Returns:
        bool: True if download successful, False otherwise.
    """
    print(f"\n--- Downloading {file_path_in_repo} from GitHub ---")
    raw_url = f"{repo_url}/raw/{branch}/{file_path_in_repo}"
    try:
        response = requests.get(raw_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        with open(local_save_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Successfully downloaded {file_path_in_repo} to {local_save_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {file_path_in_repo} from GitHub: {e}")
        print(f"Could not reach {raw_url}. Please check internet connection or repository/branch details.")
        return False
    finally:
        print(f"--- Download of {file_path_in_repo} complete ---")


def install_requirements():
    """
    Downloads the latest requirements.txt from GitHub and installs Python dependencies.
    """
    print("\n--- Preparing to install Python dependencies ---")

    # Step 1: Download the latest requirements.txt from GitHub
    success = download_file_from_github(
        GITHUB_REPO_URL,
        GITHUB_BRANCH,
        "requirements.txt",
        TEMP_REQUIREMENTS_FILE
    )

    if not success:
        print("Could not download requirements.txt. Aborting installation.")
        sys.exit(1)

    # Step 2: Install dependencies using the downloaded file
    run_command(f"{sys.executable} -m pip install -r {TEMP_REQUIREMENTS_FILE}", "Installing Python dependencies")

    # Step 3: Clean up the temporary requirements file
    try:
        os.remove(TEMP_REQUIREMENTS_FILE)
        print(f"Cleaned up temporary file: {TEMP_REQUIREMENTS_FILE}")
    except OSError as e:
        print(f"Error cleaning up temporary file {TEMP_REQUIREMENTS_FILE}: {e}")


def check_for_updates():
    """Checks for updates from the specified GitHub repository."""
    print("\n--- Checking for updates from GitHub ---")
    try:
        # Get the current commit hash of the local repository (if it's a git repo)
        try:
            local_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=os.getcwd(),
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()
            print(f"Local commit: {local_commit}")
        except subprocess.CalledProcessError:
            print("Not a Git repository, or git command not found. Cannot check local commit.")
            local_commit = None

        # Fetch the latest commit hash from the remote GitHub branch
        api_url = f"https://api.github.com/repos/{GITHUB_REPO_URL.split('/')[-2]}/{GITHUB_REPO_URL.split('/')[-1]}/branches/{GITHUB_BRANCH}"
        print(f"Checking remote URL: {api_url}")
        response = requests.get(api_url)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        remote_commit = response.json()['commit']['sha']
        print(f"Remote commit: {remote_commit}")

        if local_commit and local_commit == remote_commit:
            print("Your local repository is up to date with the remote.")
        elif local_commit and local_commit != remote_commit:
            print("A new version is available! Please consider pulling the latest changes:")
            print(f"  git pull origin {GITHUB_BRANCH}")
        else:
            print("Cannot compare commits effectively. To ensure you have the latest code, please clone or pull:")
            print(f"  git clone {GITHUB_REPO_URL}.git")
            print(f"  git pull origin {GITHUB_BRANCH}")

    except requests.exceptions.RequestException as e:
        print(f"Error checking for updates: Could not reach GitHub API. {e}")
        print("Please check your internet connection or the repository URL.")
    except KeyError:
        print("Error parsing GitHub API response. Repository or branch might not exist.")
    print("--- Update check complete ---")


def main():
    """Main function to orchestrate the installation and update checks."""
    print("Starting GPU Monitor App setup...")

    # Step 1: Install Python requirements (now downloads requirements.txt first)
    install_requirements()

    # Step 2: Check for updates (optional, but good for users)
    check_for_updates()

    print("\nSetup complete! You can now run your GPU Monitor App:")
    print("  python app.py")

if __name__ == "__main__":
    main()