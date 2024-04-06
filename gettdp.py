import requests
import platform

# Compute the average TDP for a given dictionary of processors
def compute_average_tdp(processor_dict):
    total_tdp = 0
    num_processors = 0
    for processor, tdp in processor_dict.items():
        total_tdp += tdp
        num_processors += 1
    average_tdp = total_tdp / num_processors
    return average_tdp

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

    # Check if the processor name contains "Intel", "AMD", or "M1" or "M2"
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
            return {intel_dict[processorInfo]}
        else:
            print (f"Average TDP for Intel processors: {avg_intel_tdp}")
            return {avg_intel_tdp}
    if processor.find("AMD") != -1:
        print("AMD found")
        print ("average tdp for AMD processors: ", compute_average_tdp(amd_dict))
        return {compute_average_tdp(amd_dict)}
    if processor.find("M1") != -1 or processor.find("M2") != -1:
        print("Mac found")
        if (processor.find("M1") != -1):
            return {mac_dict["M1"]}
        elif (processor.find("M2") != -1):
            return {mac_dict["M2"]}
        else:
            return {compute_average_tdp(mac_dict)}
        


import cpuinfo
import re
# Get the CPU name
cpu_name = cpuinfo.get_cpu_info()['brand_raw']
print(cpu_name)
# cpu_name = "12th Gen Intel(R) Core(TM) i7-1265U"
# cpu_name = "AMD Ryzen 5 5600"
# cpu_name = "AMD Ryzen 9 7950X"
# cleaned_cpu_name = re.sub(r'\([^)]*\)', '', cpu_name)
# print (cleaned_cpu_name)
tdp = get_tdp_from_csv('CPU__TDP_by_popularity.csv', cpu_name)
print(tdp)
