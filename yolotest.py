import subprocess
import time

def run_script_in_new_terminal(script_name):
    """
    Opens a new terminal window and runs the given script.
    """
    # Command to open a new terminal window and run the script
    command = f"gnome-terminal -- python3 {script_name}"
    
    # Run the command in the background
    subprocess.Popen(command, shell=True)

def main():
    # Path to the first script
    script1 = "heat_map_plotter.py"  # Replace with the path to your first script
    
    # Path to the second script
    script2 = "opencv.py"  # Replace with the path to your second script

    # Run both scripts in separate terminals
    run_script_in_new_terminal(script1)
    time.sleep(1)  # Ensure there is a slight delay between opening terminals
    run_script_in_new_terminal(script2)

    print("Both scripts are running in separate terminals!")

if __name__ == "__main__":
    main()

