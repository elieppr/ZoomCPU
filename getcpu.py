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
import cpuinfo
import re

class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)

# Compute the average TDP for a given dictionary of processors
def compute_average_tdp(processor_dict):
    total_tdp = 0
    num_processors = 0
    for processor, tdp in processor_dict.items():
        total_tdp += tdp
        num_processors += 1
    average_tdp = total_tdp / num_processors
    return int(average_tdp)

# Get the TDP value from a CSV file and the processor name
def get_tdp_from_csv(csv_file, processor):
    import csv
    import re
    # Initialize empty dictionaries for Intel, AMD, and Mac processors
    intel_dict = {}
    amd_dict = {}
    mac_dict = {}

    # Open the CSV file and build dictionaries for Intel, AMD, and Mac processors
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            processor_name = row[0].strip('"').replace('\r', '').replace('\r\n', '').replace('\n', '')
            processor_value = int(row[1])
            if processor_name:  # Check if processor_name is not empty        
                if "Intel" in processor_name:
                    intel_dict[processor_name] = processor_value
                elif "AMD" in processor_name:
                    amd_dict[processor_name] = processor_value
                else:
                    mac_dict[processor_name] = processor_value

    # Check if the processor name contains "Intel"
    if (processor.find("Intel") != -1):
        print("Intel found")
        try:
            # Regular expression pattern to match "Intel", "Core", and "i7-1265U"
            pattern = r'\b(Intel|Core|i7-\d{4}[A-Za-z]*)\b'
            # Extracting the desired substrings using regex
            matches = re.findall(pattern, processor)
            processorInfo = matches[0] + " " + matches[1] + " " + matches[2]
        except:
            print("Error: Processor not found in dictionary")
            processorInfo = "Intel"
        # Compute average TDP for Intel processors
        avg_intel_tdp = compute_average_tdp(intel_dict)
        
        if processorInfo in intel_dict: 
            print(f"TDP for {processorInfo}: {intel_dict[processorInfo]}")   
            return intel_dict[processorInfo]
        else:
            print (f"Average TDP for Intel processors: {avg_intel_tdp}")
            return avg_intel_tdp
    # Check if the processor name contains "AMD"
    elif processor.find("AMD") != -1:
        print("AMD found")
        print ("average tdp for AMD processors: ", compute_average_tdp(amd_dict))
        return compute_average_tdp(amd_dict)
    # Check if the processor name contains "M1" or "M2"
    elif processor.find("M1") != -1 or processor.find("M2") != -1:
        print("Mac found")
        if (processor.find("M1") != -1):
            return mac_dict["M1"]
        elif (processor.find("M2") != -1):
            return mac_dict["M2"]
        else:
            return compute_average_tdp(mac_dict)
    else:
        return 95
        
def delete_file(file_path):
    # Check if the file exists, Delete the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"The file '{file_path}' has been deleted.")
    else:
        print(f"The file '{file_path}' does not exist.")


def monitor_cpu_usage():
    # Delete existing files
    delete_file("zoom.yml")
    delete_file("zoomOutput.yml")
    delete_file("zoomOutput.csv")
    delete_file("trend_plot.html")

    # Initialize an empty list to store the input data
    input = []
    # Read the contents of zoombase.yml
    with open("zoombase.yml", "r") as f:
        data = yaml.safe_load(f)

    # Get the CPU name and TDP value
    cpu_name = cpuinfo.get_cpu_info()['brand_raw']
    tdp = get_tdp_from_csv('CPU__TDP_by_popularity.csv', cpu_name)
    print("TDP value:", tdp)

    # Add the input data to the list
    while True:
        # Get a list of zoom processes information
        zoom_processes = get_zoom_processes()
        
        total_cpu = 0
        if not zoom_processes:  # Check if zoom_processes is empty
            print("Zoom meeting ended. Exiting loop.")
            break  # Exit the loop if zoom_processes is empty

        # Calculate the total CPU usage of all Zoom processes
        for proc in zoom_processes:
            pid = proc.info['pid'] 
            name = proc.info['name']
            try:
                cpu_usage = get_process_cpu_usage(pid)
                total_cpu += cpu_usage   
                # Adjust the total CPU usage for macOS
                if platform.system() == 'Darwin':
                    total_cpu /= os.cpu_count() 
                # Print the CPU usage of each Zoom process            
                if cpu_usage is not None:
                    print("CPU usage of process '{}' (PID: {}): {:.2f}%".format(name, pid, cpu_usage))     
            except Exception as e:
                # If the process is not found, skip it
                continue

        if total_cpu > 0:
            input.append({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), 
                          "duration": 10, 
                          "cpu/thermal-design-power": tdp, 
                          "cloud/region-wt-id": "CAISO_NORTH", 
                          "geolocation": "37.7749,-122.4194",
                          "cpu/utilization": total_cpu
                          })
        # Wait for 10 seconds before checking the CPU usage again
        time.sleep(10)

    # Add the input data to the yaml file
    data["tree"]["children"]["child-0"]["inputs"] = input

    # Write the input data to the yaml file
    with open("zoom.yml", "a") as f:
        yaml.dump(data, f, Dumper=IndentDumper)

def get_zoom_processes():
    # Get a list of all running processes
    all_processes = psutil.process_iter(['pid', 'name'])
    # Filter the list to get only the Zoom processes
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
    cpu_percent = process.cpu_percent(interval=1.0) 
    return cpu_percent

def create_plot(data_column, title, xtitle, df):
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
        margin=dict(l=50, r=50, t=50, b=50), 
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                layer="below",
                line=dict(width=0),
            )
        ]
    )
    return fig

def generate_csv():
    import csv
    from datetime import datetime, timedelta
    # Read the YAML file
    with open("zoomOutput.yaml", "r") as file:
        data = yaml.safe_load(file)
        csvoutputs = data["tree"]["children"]["child-0"]["outputs"]
        # Write the data to a CSV file
        with open("zoomOutput.csv", "w", newline='') as file:
            writer = csv.writer(file)
            headers = list(csvoutputs[0].keys())
            headers.append("cpu/carbon")  # Add a new column header
            writer.writerow(headers)
            # Initialize previous grid_carbon_intensity and timestamp
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
                        grid_carbon_intensity = prev_grid_carbon_intensity
                        item["grid/carbon-intensity"] = grid_carbon_intensity
                cpu_carbon = cpu_energy * grid_carbon_intensity  # Calculate cpu/carbon
                item["cpu/carbon"] = cpu_carbon  # Add cpu/carbon to the item dictionary
                # Write the item values to the CSV file
                writer.writerow(item.values())
 
def generate_html(html_file='trend_plot.html'):
    # Read the CSV file
    df = pd.read_csv('zoomOutput.csv')
    # Convert timestamp column to datetime type if it's not already in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Create a plot for energy and carbon emissions
    fig1 = create_plot('cpu/energy', 'Energy Consumption (kWh)', 'Energy', df)
    fig2 = create_plot('cpu/carbon', 'Carbon Emission (gCO2)', 'Carbon', df)
    # Get the current working directory
    current_directory = os.getcwd()
    imagefull_path1 = os.path.join(current_directory, 'caremission.png')
    imagefull_path2 = os.path.join(current_directory, 'phonecharge.png')
    imagefull_path3 = os.path.join(current_directory, 'carbonatedDrink.png')
    # Get machine information
    num_cores_os = os.cpu_count()
    processor_info = platform.processor()
    architecture = platform.architecture()
 
    # Get the minimum and maximum values of the timestamp column
    min_timestamp = df['timestamp'].min()
    max_timestamp = df['timestamp'].max()
    # Calculate the total energy and carbon emissions
    total_energy = (df['cpu/energy'].sum() - 0.5 * (df['cpu/energy'].iloc[0] + df['cpu/energy'].iloc[-1]))*10
    total_carbon = (df['cpu/carbon'].sum() - 0.5 * (df['cpu/carbon'].iloc[0] + df['cpu/carbon'].iloc[-1]))*10
        
    summary = "Your zoom meeting lasted from " + str(min_timestamp) + " to " + str(max_timestamp) + ". The total carbon consumed during the meeting is " + str("{:.2f}".format(total_carbon)) + " gCO2, and the total energy consumed is " + str("{:.2f}".format(total_energy)) + " kWh. "
    machine_info = "Here are some details about your machine: \n Processor: " + processor_info + "\nArchitecture: " + architecture[0] + " " + architecture[1] + "\nNumber of CPU cores: " + str(num_cores_os)

    with open(html_file, 'w') as f:
        f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout

        f.write('<div style="width: 60%;">')  # Left side for the plot
        f.write(fig1.to_html(include_plotlyjs='cdn'))  # Plotly graph
        f.write(fig2.to_html(include_plotlyjs='cdn'))  # Plotly graph
        f.write('</div>')  # End of left div

        # Conversions for pictures
        carbDrinks = total_carbon/2.5 ## source: https://www.sciencefocus.com/science/does-the-carbon-dioxide-released-from-fizzy-drinks-affect-the-atmosphere  
        phoneCharge = total_energy*0.066 ## source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator#results 
        carEmissionMiles = total_carbon*0.003 ## source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator#results
        carEmissionsKm = carEmissionMiles*1.60934 ## source: https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator#results


        ####### ================== right panel ================== #######
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

        f.write('</div>')  # End of flex div


# Main function
if __name__ == "__main__":
    # Monitor the CPU usage of the Zoom processes
    monitor_cpu_usage()
    
    # Run the IE command to generate the output
    if os.name == 'nt':
        ###------ Windows ------###
        print('Windows')
        # Define the directory containing npx
        nodejs_path = "C:\\Program Files\\nodejs"
        npx_path = os.path.join(nodejs_path, "npx.cmd")
        
        command = [npx_path,"ie",  "--manifest", ".\\zoom.yml", "--output", ".\\zoomOutput"]
        
        # Call the command using subprocess.run()
        result = subprocess.run(command, capture_output=True, text=True)
    
    else:
        ###------ MacOS ------###
        print('MacOS')
        # Define the directory containing npx
        nodejs_path = "/usr/local/bin"
        npx_path = os.path.join(nodejs_path, "npx")

        command = [npx_path,"ie",  "--manifest", "zoom.yml", "--output", "zoomOutput"]

        # Call the command using subprocess.run()
        result = subprocess.run(command, capture_output=True, text=True)

    generate_csv()

    # Generate and save the plot as an HTML file
    html_file = 'trend_plot.html'
    generate_html(html_file=html_file)

    # Get the current working directory
    current_directory = os.getcwd()
    full_path = os.path.join(current_directory, html_file)

    # Open the HTML file in a web browser
    webbrowser.open('file://' + full_path)




