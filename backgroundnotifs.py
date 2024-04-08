import psutil
import os
import time
import yaml
import subprocess
import shutil
from plyer import notification
from datetime import datetime
import time

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="Zoom",
        timeout=10  # Notification will stay for 10 seconds
    )

THRESHOLD = int(input("Enter the threshold: "))

class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)

import os

def delete_file(file_path):
    """
    Delete the specified file if it exists.

    Parameters:
    - file_path (str): Path to the file to be deleted.
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"The file '{file_path}' has been deleted.")
    else:
        print(f"The file '{file_path}' does not exist.")

def current_milli_time():
    return round(time.time() * 1000)

def monitor_cpu_usage():
    delete_file("zoom.yml")
    delete_file("zoomOutput.yml")
    delete_file("zoomOutput.csv")

    input = []
    # Step 2: Read the contents of zoom.yml
    with open("project.yml", "r") as f:
        data = yaml.safe_load(f)

    for x in range(60 // 4):
        zoom_processes = get_zoom_processes()

        total_cpu = 0
        time1 = current_milli_time()

        for proc in zoom_processes:
            # Get process ID and name
            pid = proc.info['pid'] 
            name = proc.info['name']
            try:
                cpu_usage = get_process_cpu_usage(pid)
                total_cpu += cpu_usage                
            except Exception as e:
                print(f"Error occurred while getting CPU usage of process '{name}' (PID: {pid}): {str(e)}")
                continue  # Continue to the next iteration of the loop
        if total_cpu > 0:
            x = datetime.now()
            # Round down the minutes to the nearest multiple of 5
            rounded_minutes = x.minute - (x.minute % 5)
            rounded_time = x.replace(minute=rounded_minutes, second=0, microsecond=0)
            rounded_time_str = rounded_time.strftime("%Y-%m-%dT%H:%M")
            total_cpu = min(100, total_cpu)
            print("Zoom CPU:", "%.2f" % total_cpu)
            input.append({"timestamp": rounded_time_str, "duration": 4, "cpu/utilization": total_cpu, "cpu/thermal-design-power": 15})

        time2 = current_milli_time()
        time.sleep(max(0, (4000 - (time2 - time1)) / 1000))

    data["tree"]["children"]["application"]["inputs"] = input

    with open("zoom.yml", "a") as f:
        # yaml.dump(input, f, indent=8)
        yaml.dump(data, f, Dumper=IndentDumper)


def get_all_process():
    # Get a list of all running processes
    return psutil.process_iter(['pid', 'name'])

def get_zoom_processes():
    # Get a list of all running processes
    all_processes = psutil.process_iter(['pid', 'name'])

    # Filter processes to a specific name
    return [i for i in all_processes if i.info['name'] == 'Zoom.exe']


def get_process_cpu_usage(process_id):
    # Check if the process exists
    if not psutil.pid_exists(process_id):
        print("Process with PID {} does not exist.".format(process_id))
        return None
    
    # Get the process object
    process = psutil.Process(process_id)
    
    # Get CPU usage
    cpu_percent = process.cpu_percent(interval=1.0)  # You can adjust the interval as needed
    
    return cpu_percent

# Example usage
if __name__ == "__main__":
    while True: 
        print("List of all running process names:")
        monitor_cpu_usage()

        # switch between Windows and MacOS
        if os.name == 'nt':
            ###------ Windows ------###
            print('Running command: ie --manifest .\\zoom.yml --output .\\zoomOutput')
            # Define the directory containing npx
            nodejs_path = "C:\\Program Files\\nodejs"
            npx_path = os.path.join(nodejs_path, "npx.cmd")
            
            command = [npx_path,"ie",  "--manifest", ".\\zoom.yml", "--output", ".\\zoomOutput"]

            # Call the command using subprocess.run()
            result = subprocess.run(command, capture_output=True, text=True)

            with open("zoomOutput.yaml", "r") as f:
                data = yaml.safe_load(f)
            energy = []
            intensity = []
            for i in data['tree']['children']['application']['outputs']:
                try:
                    energy.append(i['cpu/energy'])
                except:
                    energy.append(0)
                intensity.append(i['grid/carbon-intensity'])
            carbon = sum([energy[i] * intensity[i] for i in range(len(energy))]) * 1000

            if carbon >= THRESHOLD:
                send_notification("Warning: high zoom carbon emissions", f"Your carbon emissions were at {'%.2f' % carbon} mg, which passes the threshold of {THRESHOLD}.")
        
        else:
            ###------ MacOS ------###
            print('MacOS')
            
            # Define the directory containing npx
            nodejs_path = "/usr/local/bin"
            npx_path = os.path.join(nodejs_path, "npx")

            # Define the command as a list of strings
            command = [npx_path,"ie",  "--manifest", "zoom.yml", "--output", "zoomOutput"]

            # Call the command using subprocess.run()
            result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            print("Command executed successfully.")
            print("Output:")
            print(result.stdout)
        else:
            print("Error executing the command:")
            print(result.stderr)