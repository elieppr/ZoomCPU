import psutil
import os
import time
import yaml
import subprocess
import shutil
import pandas as pd
import plotly.graph_objs as go
import webbrowser
import csv
import multiprocessing
import platform

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
    delete_file("trend_plot.html")

    input = []
    # Step 2: Read the contents of zoom.yml
    with open("zoombase.yml", "r") as f:
        data = yaml.safe_load(f)

    print(data)

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
                
                if platform.system() == 'Darwin': # macOS
                    total_cpu /= os.cpu_count()             
                if cpu_usage is not None:
                    print("CPU usage of process '{}' (PID: {}): {:.2f}%".format(name, pid, cpu_usage))   
            except Exception as e:
                print(f"Error occurred while getting CPU usage of process '{name}' (PID: {pid}): {str(e)}")
                continue  # Continue to the next iteration of the loop
        if total_cpu > 0:
            import random
            random_number = random.randint(50, 100)
            input.append({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), 
                          "duration": 10, 
                          "cpu/thermal-design-power": 20, 
                          "cloud/region": "westus", 
                          "cloud/region-wt-id": "CAISO_NORTH", 
                          "geolocation": "37.7749,-122.4194",
                          "cpu/utilization": total_cpu
                          #"cpu/utilization": random_number
                          })

        time.sleep(10)

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
    # if os.name == 'nt':
    #     zoom_processes = [proc for proc in all_processes if "Zoom" in proc.info['name']]
    # else:   # For MacOS
    #     zoom_processes = [proc for proc in all_processes if "zoom" in proc.info['name']]

    zoom_processes = [proc for proc in all_processes if "zoom" in proc.info['name'].lower()]
    
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

def create_plot(data_column, title, xtitle):
    # Create a plotly figure
    fig = go.Figure()

    # Add a scatter plot with time as x-axis and value as y-axis
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df[data_column], mode='lines+markers'))

    # Update layout to set width and height
    fig.update_layout(
        title= title, # 'Carbon Emission',
        title_x=0.5,  # Center the title
        xaxis_title='Time',
        yaxis_title= xtitle, #'Carbon',
        width=1100,  # Set width to 50%
        height=500,  # Set height to 50%
        margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins to make space for the paragraph on the right
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                #fillcolor="rgba(0, 255, 0, 0.2)",  # Green with 20% opacity
                layer="below",
                line=dict(width=0),
            )
        ]
    )
    return fig

def generate_csv():
    import csv
    from datetime import datetime, timedelta
 
    with open("zoomOutput.yaml", "r") as file:
        data = yaml.safe_load(file)
        csvoutputs = data["tree"]["children"]["child-0"]["outputs"]
 
        with open("zoomOutput.csv", "w", newline='') as file:
            writer = csv.writer(file)
            headers = list(csvoutputs[0].keys())
            headers.append("cpu/carbon")  # Add a new column header
            writer.writerow(headers)
 
            prev_grid_carbon_intensity = None
            prev_timestamp = None
 
            for item in csvoutputs:
                cpu_energy = item["cpu/energy"]
                grid_carbon_intensity = item["grid/carbon-intensity"]
                # Update previous non-zero grid_carbon_intensity and timestamp
                if grid_carbon_intensity != 0:
                    prev_grid_carbon_intensity = grid_carbon_intensity
                    prev_timestamp = datetime.strptime(item["timestamp"], "%Y-%m-%dT%H:%M:%S")
 
                # Check if grid_carbon_intensity is zero and if the previous non-zero value exists
                if grid_carbon_intensity == 0 and prev_grid_carbon_intensity is not None:
                    # Check if the difference in timestamps is less than 5 minutes
                    if prev_timestamp and (datetime.strptime(item["timestamp"], "%Y-%m-%dT%H:%M:%S") - prev_timestamp) < timedelta(minutes=5):
                    #if prev_timestamp and (item["timestamp"] - prev_timestamp) < timedelta(minutes=5):
                        grid_carbon_intensity = prev_grid_carbon_intensity
                        item["grid/carbon-intensity"] = grid_carbon_intensity
                cpu_carbon = cpu_energy * grid_carbon_intensity  # Calculate cpu/carbon
                item["cpu/carbon"] = cpu_carbon  # Add cpu/carbon to the item dictionary
 
                writer.writerow(item.values())
 

# Example usage
if __name__ == "__main__":
    print("List of all running process names:")
    monitor_cpu_usage()
    # Define the directory containing npx
   
    # switch between Windows and MacOS
    if os.name == 'nt':
        ###------ Windows ------###
        print('Windows')
        # Define the directory containing npx
        nodejs_path = "C:\\Program Files\\nodejs"
        npx_path = os.path.join(nodejs_path, "npx.cmd")
        
        #command = ["C:\\Users\\Eliana\\AppData\\Roaming\\npm\\ie.cmd", "--manifest", "C:\\Users\\Eliana\\Documents\\GitHub\\if\\examples\\manifests\\co2js.yml", "--output", "C:\\Users\\Eliana\\Documents\\GitHub\\if\\examples\\manifests\\co2outputIE.yml"]
        command = [npx_path,"ie",  "--manifest", ".\\zoom.yml", "--output", ".\\zoomOutput"]
        #command = [npx_path,"ie",  "--manifest", ".\\basic.yml", "--output", ".\\zoomOutput"]

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
 
    
    # with open("zoomOutput.yaml", "r") as file:
    #     data = yaml.safe_load(file)
    #     csvoutputs = data["tree"]["children"]["child-0"]["outputs"]

    #     with open("zoomOutput.csv", "w", newline='') as file:
    #         writer = csv.writer(file)
    #         headers = list(csvoutputs[0].keys())
    #         headers.append("cpu/carbon")  # Add a new column header
    #         writer.writerow(headers)

    #         for item in csvoutputs:
    #             cpu_energy = item["cpu/energy"]
    #             grid_carbon_intensity = item["grid/carbon-intensity"]
    #             cpu_carbon = cpu_energy * grid_carbon_intensity  # Calculate cpu/carbon
    #             item["cpu/carbon"] = cpu_carbon  # Add cpu/carbon to the item dictionary
    #             writer.writerow(item.values())
    generate_csv()


    # Read the CSV file
    df = pd.read_csv('zoomOutput.csv')
    fig1 = create_plot('cpu/energy', 'Energy Consumption (kWh)', 'Energy')
    fig2 = create_plot('cpu/carbon', 'Carbon Emission (gCO2)', 'Carbon')

  
current_directory = os.getcwd()
imagefull_path1 = os.path.join(current_directory, 'caremission.png')
imagefull_path2 = os.path.join(current_directory, 'phonecharge.png')
imagefull_path3 = os.path.join(current_directory, 'carbonatedDrink.png')

another_image_full_path = os.path.join(current_directory, 'gsf.png')


# Method 1: Using os.cpu_count()
num_cores_os = os.cpu_count()
processor_info = platform.processor()
architecture = platform.architecture()


print("Number of CPU cores (Method 1):", num_cores_os)

message = "number of CPU is " + str(num_cores_os)

# Read the CSV file
df = pd.read_csv('zoomOutput.csv')

# Convert timestamp column to datetime type if it's not already in datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Get the minimum and maximum values of the timestamp column
min_timestamp = df['timestamp'].min()
max_timestamp = df['timestamp'].max()

#total_energy = df['cpu/energy'].sum()
total_energy = (df['cpu/energy'].sum() - 0.5 * (df['cpu/energy'].iloc[0] + df['cpu/energy'].iloc[-1]))*10
# total_carbon = df['cpu/carbon'].sum()
total_carbon = (df['cpu/carbon'].sum() - 0.5 * (df['cpu/carbon'].iloc[0] + df['cpu/carbon'].iloc[-1]))*10

# Save the plot as an HTML file
html_file = 'trend_plot.html'
    
summary = "Your zoom meeting lasted from " + str(min_timestamp) + " to " + str(max_timestamp) + ". The total carbon consumed during the meeting is " + str("{:.2f}".format(total_carbon)) + " gCO2, and the total energy consumed is " + str("{:.2f}".format(total_energy)) + " kWh. "

machine_info = "Here are some details about your machine: \n Processor: " + processor_info + "\nArchitecture: " + architecture[0] + " " + architecture[1] + "\nNumber of CPU cores: " + str(num_cores_os)

with open(html_file, 'w') as f:
    f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
    
    f.write('<div style="width: 60%;">')  # Left side for the plot
    f.write(fig1.to_html(include_plotlyjs='cdn'))  # Plotly graph
    f.write(fig2.to_html(include_plotlyjs='cdn'))  # Plotly graph
    f.write('</div>')  # End of left div

    #conversions for pictures
    carbDrinks = total_carbon/2.5 ## source: https://www.sciencefocus.com/science/does-the-carbon-dioxide-released-from-fizzy-drinks-affect-the-atmosphere  
    phoneCharge = total_energy*0.066 ## source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator#results 
    carEmissionMiles = total_carbon*0.003 ## source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator#results
    carEmissionsKm = carEmissionMiles*1.60934 ## source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator#results


####### ======================= right panel =======================
    f.write('<div style="width: 30%;">')  # Right side for the paragraph
    f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
    f.write('<p style="margin-top: 20px; margin-right: 20px">' + summary + '</p>')  # Description paragraph adjusted 50px lower
    f.write('<p style="margin-top: 20px; margin-right: 10px">' + machine_info +'</p>')  # Description paragraph
    f.write('</div>')  # End of flex div

    f.write('<div style="margin-right: 30px;">')  # Margin for spacing between images
    f.write('<img src=' + imagefull_path1 + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 1
    f.write('<p>This is equivalent to ' + str("{:.3f}".format(carEmissionsKm)) + ' Km (' + str("{:.3f}".format(carEmissionMiles)) + ' Miles) driven by an average gasoline-powered passenger vehicle.</p>')  # Caption for Image 1
    f.write('</div>')  # End of div for Image 1

    f.write('<div style="margin-right: 30px;">')  # Margin for spacing between images
    f.write('<img src=' + imagefull_path2 + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 2
    f.write('<p>This is equivalent to ' + str("{:.3f}".format(phoneCharge)) + ' smartphones charged.</p>')  # Caption for Image 2
    f.write('</div>')  # End of div for Image 2

    f.write('<div>')  # No margin for the last image
    f.write('<img src=' + imagefull_path3 + ' alt="Image" style="width: 360px; margin-top: 20px;">')  # Image 3
    f.write('<p>This is equivalent to emissions from ' + str("{:.3f}".format(carbDrinks)) + ' carbonated drinks.</p>')  # Caption for Image 3
    f.write('</div>')  # End of div for Image 3

####### ======================= bottom panel =======================


    f.write('</div>')  # End of flex div


# Get the current working directory
current_directory = os.getcwd()
full_path = os.path.join(current_directory, html_file)

# Open the HTML file in a web browser
webbrowser.open('file://' + full_path)




