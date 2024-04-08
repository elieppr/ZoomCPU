# ZoomCPU
Hackathon for Green Software Foundation

In this Hackathon project we used python to get the cpu of a Zoom meeting and convert it to energy and carbon emissions during a zoom meeting, for both Windows and Mac OS

## There are two basic functionalities:
## getcpu.py: get the cpu usage of Zoom and display the cpu/energy, cpu/carbon in an html file:
    - get the Zoom process and the CPU using psutil
    - combine the cpu usage with the predefined manifest "zoombase.yml" and create a new manifest input file: zoom.yml
    - invoke IF framework (calling ie --manifest zoombase.yml --out zoomOutput) create output zoomOutput.yaml
    - extract zoomOutput.yaml file output and convert to zoomOutput.csv file
    - generate an html file based on the data in zoomOutput.csv and automatically display it in the browser. The html file contains a plot of cpu/energy vs timestamp and cpu/carbon vs timestamp together with total carbon consumption.

## backgroundnotifs.py: send a python notification when the Zoom meeting carbon emission is over the threshold you defind.
    Similar to above, but for every minute, and instead of generating an html file, it sends a notification if carbon exceeds the threshold, measured in milligrams. This one can be run in the background or together with the above functionality as well.

## Getting started:
```sh
    npm install -g "@grnsft/if" 
    npm install -g "@grnsft/if-plugins"
    npm install -g "@if-unofficial-plugins"
    pip install psutil
    pip install pyyaml
    pip install pandas
    pip install plotly
    pip install cpuinfo
    pip install plyer
```    

## To run the program:
    - Start Zoom meeting
    - run the following in two different sessions (you can either run both or one of them)
```sh    
        python getcpy.py
```    

```sh    
        python backgroundnotifs.py
```    

            - this one will prompty to ask to input THRESHOLD, input your threshold as desired
