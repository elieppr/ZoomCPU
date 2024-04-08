import psutil
import os
import time
import yaml
import subprocess
from plyer import notification
import time
from datetime import datetime
from getcpu import *

def send_notification(title, message):
    # if the OS is Windows
    if os.name == 'nt':
        notification.notify(
            title=title,
            message=message,
            app_name="Zoom",
            timeout=10  # Notification will stay for 10 seconds
        )
    else: # if the OS is MacOSç
        # Define the command as a string
        script = f'display notification "{message}" with title "{title}"'
        # Call the command using subprocess.run()
        subprocess.run(['osascript', '-e', script])

THRESHOLD = int(input("Enter the threshold: "))

def current_milli_time():
    return round(time.time() * 1000)

def monitor_cpu_usage():
    delete_file("zoomNotification.yml")

    cpu_name = cpuinfo.get_cpu_info()['brand_raw']
    tdp = get_tdp_from_csv('CPU__TDP_by_popularity.csv', cpu_name)

    delete_file("zoomNotificationOutput.yml")
    delete_file("zoomNotificationOutput.csv")

    input = []
    # Read the contents of zoombase.yml
    with open("zoombase.yml", "r") as f:
        data = yaml.safe_load(f)

    # get the CPU usage every 4 seconds for 1 minute
    for x in range(60 // 4):
        zoom_processes = get_zoom_processes()

        if not zoom_processes:  # Check if zoom_processes is empty
            print("Zoom meeting ended. Exiting the notification program.")
            import sys
            sys.exit()  # Exit the program if zoom_processes is empty

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
                print(f"Cannot get CPU usage of process '{name}' (PID: {pid}): {str(e)}")
                continue  # Continue to the next iteration of the loop
        if total_cpu > 0:
            x = datetime.now()
            # Round down the minutes to the nearest multiple of 5
            rounded_minutes = x.minute - (x.minute % 5)
            rounded_time = x.replace(minute=rounded_minutes, second=0, microsecond=0)
            rounded_time_str = rounded_time.strftime("%Y-%m-%dT%H:%M")
            total_cpu = min(100, total_cpu)
            print("Zoom CPU:", "%.2f" % total_cpu)
            input.append({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), 
                "duration": 4, 
                "cpu/thermal-design-power": tdp, 
                "cloud/region-wt-id": "CAISO_NORTH", 
                "geolocation": "37.7749,-122.4194",
                "cpu/utilization": total_cpu
                })

        time2 = current_milli_time()
        time.sleep(max(0, (4000 - (time2 - time1)) / 1000))

    # Add the input data to the yaml file
    data["tree"]["children"]["child-0"]["inputs"] = input

    with open("zoomNotification.yml", "a") as f:
        yaml.dump(data, f, Dumper=IndentDumper)


# Main
if __name__ == "__main__":
    while True: 
        # Monitor the CPU usage
        monitor_cpu_usage()

        
        if os.name == 'nt':
            ###------ Windows ------###
            print('Running command: ie --manifest .\\zoomNotification.yml --output .\\zoomNotificationOutput')
            # Define the directory containing npx
            nodejs_path = "C:\\Program Files\\nodejs"
            npx_path = os.path.join(nodejs_path, "npx.cmd")
            
            command = [npx_path,"ie",  "--manifest", ".\\zoomNotification.yml", "--output", ".\\zoomNotificationOutput"]

            # Call the command using subprocess.run()
            result = subprocess.run(command, capture_output=True, text=True)

        else:
            ###------ MacOS ------###
            print('MacOS')
            
            # Define the directory containing npx
            nodejs_path = "/usr/local/bin"
            npx_path = os.path.join(nodejs_path, "npx")

            # Define the command as a list of strings
            command = [npx_path,"ie",  "--manifest", "zoomNotification.yml", "--output", "zoomNotificationOutput"]

            # Call the command using subprocess.run()
            result = subprocess.run(command, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            print("Command executed successfully.")
            print("Output:")
            print(result.stdout)

            # Generate the CSV file from the output YAML file
            generate_csv("zoomNotificationOutput.yaml", "zoomNotificationOutput.csv")

            # get the carbon emissions from the CSV file
            df = pd.read_csv('zoomNotificationOutput.csv')
            carbon = (df['cpu/carbon'].sum() - 0.5 * (df['cpu/carbon'].iloc[0] + df['cpu/carbon'].iloc[-1]))*10*1000
            print ("comuted carbon = ", carbon) 

            # Send notification if the carbon emissions exceed the threshold
            if int(carbon) >= int(THRESHOLD):
                send_notification("Warning: high zoom carbon emissions", f"Your carbon emissions were at {'%.2f' % carbon} mg, which passes the threshold of {THRESHOLD}.")
        
        else:
            print("Error executing the command:")
            print(result.stderr)
