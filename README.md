# ZoomCPU

## Hackathon for Green Software Foundation

In this Hackathon project we implement python which can take the cpu of Zoom meeting convert to cpu energy and carbon emission during the zoom meeting, for both Windows and Mac OS

There are two basic functionlity:
getcpu.py: get the cpu usage of Zoom and disply the cpu/energy, cpu/carbon in a html file:
    - get the Zoom process and the CPU using psutil
    - combine the cpu usage with predefined manifest "zoombase.yml" create a new manifest input file: zoom.yml
    - invoke IF framework (calling ie --manifest zoombase.yml --out zoomOutput) create output zoomOutput.ymal
    - extract zoomOutput.ymal file output and convert to zoomOutput.csv file
    - generate html file based on the data in zoomOutput.csv and automatically display it in the browser. The html file contains plot of cpu/energy vs timestamp and cpu/carbon vs timestamp together with total carbon consumption.

backgroundnotifs.py: send a python notification when the Zoom meeting carbon emission is over the threshold you defind.
    Similar to the above functionality, but for every minute, and rather than an html file, a notification is sent if cabon exceed the threashold in milligrams. 

These two functions can be ran simultaneously.

Getting started:
    npm install -g "@grnsft/if" 
    npm install -g "@grnsft/if-plugins"
    npm install -g "@if-unofficial-plugins"
    pip install psutil
    pip install pyyaml
    pip install pandas
    pip install plotly
    pip install cpuinfo
    pip install plyer

To run the program:
    Open Zoom application
    run the following in two different sessions (you can either run both or one of them)
        python getcpy.py
        python backgroundnotifs.py
            this one will prompty to ask to input THRESHOLD, input your threshold as desired
