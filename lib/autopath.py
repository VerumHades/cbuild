import os
import sys
import platform

def add_to_path(directory):
    if platform.system() == "Windows":
        add_to_windows_path(directory)
    else:
        add_to_unix_path(directory)

def add_to_windows_path(directory):
    # Windows-specific logic to add to PATH
    current_path = os.environ.get("PATH", "")

    if directory not in current_path:
        print(f"Adding {directory} to PATH on Windows.")
        # Update the PATH permanently (this modifies the system environment variable)
        os.system(f"setx PATH \"%PATH%;{directory}\"")

def add_to_unix_path(directory):
    # Check if the directory is already in PATH
    current_path = os.environ.get("PATH", "")

    if directory not in current_path:
        print(f"Adding {directory} to PATH on Unix-based system.")
        # Determine which shell config file to modify
        shell_config_files = ["~/.bashrc", "~/.zshrc", "~/.profile"]

        # Check for which shell is used and modify the corresponding file
        for config_file in shell_config_files:
            # Expand the path if needed
            expanded_config_file = os.path.expanduser(config_file)
            if os.path.exists(expanded_config_file):
                with open(expanded_config_file, "a") as f:
                    f.write(f'\n# Added by script to include {directory} in PATH\n')
                    f.write(f'export PATH="$PATH:{directory}"\n')
                print(f"Added {directory} to {expanded_config_file}")
                break
        else:
            print("No shell config file found. Please add the directory to PATH manually.")
