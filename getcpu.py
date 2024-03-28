import psutil
import os
import time
import yaml
import subprocess
import shutil

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


def monitor_cpu_usage():
    # Copy contents of zoombase.yml to zoom.yml
    # shutil.copyfile("zoombase.yml", "zoom.yml")

    delete_file("zoom.yml")
    delete_file("zoomOutput.yml")
    delete_file("zoomOutput.csv")

    input = []
    # Step 2: Read the contents of zoom.yml
    with open("zoombase.yml", "r") as f:
        data = yaml.safe_load(f)

    while True:
        zoom_processes = get_zoom_processes()

        total_cpu = 0
        if not zoom_processes:  # Check if zoom_processes is empty
            print("Zoom meeting ended. Exiting loop.")
            break  # Exit the loop if zoom_processes is empty

        for proc in zoom_processes:
            # Get process ID and name
            pid = proc.info['pid'] 
            name = proc.info['name']
            try:
                cpu_usage = get_process_cpu_usage(pid)
                total_cpu += cpu_usage                
                if cpu_usage is not None:
                    print("CPU usage of process '{}' (PID: {}): {:.2f}%".format(name, pid, cpu_usage))   
            except Exception as e:
                print(f"Error occurred while getting CPU usage of process '{name}' (PID: {pid}): {str(e)}")
                continue  # Continue to the next iteration of the loop
        if total_cpu > 0:
            input.append({"timestamp": time.strftime("%Y-%m-%dT%H:%M"), "duration": 1, "cpu/utilization": total_cpu})
        
        # Update the data structure
        #data["tree"]["children"]["child-0"]["inputs"] = {"timestamp": time.strftime("%Y-%m-%dT%H:%M"), "duration": 10, "cpu/utilization": total_cpu}

        # Step 4: Write the updated data structure back to zoom.yml


        # # Write data to YAML file
        # with open("zoom.yml", "a") as f:
        #     timestamp = time.strftime("%Y-%m-%dT%H:%M")
        #     data = {"timestamp": timestamp, "duration": 1, "cpu/utilization": total_cpu}
        #     yaml.dump([data], f, default_flow_style=False, indent=8)

        time.sleep(1)
    data["tree"]["children"]["child-0"]["inputs"] = input

    with open("zoom.yml", "a") as f:
        # yaml.dump(input, f, indent=8)
        yaml.dump(data, f, Dumper=IndentDumper)


def get_all_process():
    # Get a list of all running processes
    all_processes = psutil.process_iter(['pid', 'name'])
    
    # Extract process names from the process objects
    # process_names = [proc.info['name'] for proc in all_processes]
    
    return all_processes

def get_zoom_processes():
    # Get a list of all running processes
    all_processes = psutil.process_iter(['pid', 'name'])
    
    # Filter processes containing "Zoom" in their name
    zoom_processes = [proc for proc in all_processes if "Crossy" in proc.info['name']]
    
    return zoom_processes


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

    #process_names = get_all_process_names()
    #zoom_processes = get_zoom_processes()
    print("List of all running process names:")
    #monitor_cpu_usage(zoom_processes)
    #
    monitor_cpu_usage()

    # Define the command as a list of strings
    #command = ["npx", "ie", "--manifest", ".\\co2js.yml", "--output", ".\\co2output.yml"]
    #command = ["C:\\Program Files\\nodejs\npx.cmd", "ie", "--manifest", "C:\\Users\\Eliana\\Documents\\GitHub\\if\\examples\\manifests\\co2js.yml", "--output", "C:\\Users\\Eliana\\Documents\\GitHub\\if\\examples\\manifests\\co2output.yml"]

    # switch between Windows and MacOS
    if os.name == 'nt':
        ###------ Windows ------###
        print('Windows')
        # Define the directory containing npx
        nodejs_path = "C:\\Program Files\\nodejs"
        npx_path = os.path.join(nodejs_path, "npx.cmd")
        
        #command = ["C:\\Users\\Eliana\\AppData\\Roaming\\npm\\ie.cmd", "--manifest", "C:\\Users\\Eliana\\Documents\\GitHub\\if\\examples\\manifests\\co2js.yml", "--output", "C:\\Users\\Eliana\\Documents\\GitHub\\if\\examples\\manifests\\co2outputIE.yml"]
        command = [npx_path,"ie",  "--manifest", ".\\zoom.yml", "--output", ".\\zoomOutput"]

        # Call the command using subprocess.run()
        result = subprocess.run(command, capture_output=True, text=True)
    
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
    


    




    


