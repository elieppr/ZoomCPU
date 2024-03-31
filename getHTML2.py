import os
import pandas as pd
import plotly.graph_objs as go
import webbrowser
import platform

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


delete_file("trend_plot.html")
current_directory = os.getcwd()
imagefull_path1 = os.path.join(current_directory, 'caremission.png')
imagefull_path2 = os.path.join(current_directory, 'phonecharge.png')
imagefull_path3 = os.path.join(current_directory, 'moofart.png')

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

total_energy = df['cpu/energy'].sum()

# Create a plotly figure
fig = go.Figure()

# Add a scatter plot with time as x-axis and value as y-axis
fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cpu/energy'], mode='lines+markers'))

# Update layout to set width and height
fig.update_layout(
    title='Carbon Emission',
    title_x=0.5,  # Center the title
    xaxis_title='Time',
    yaxis_title='Carbon',
    width=1200,  # Set width to 50%
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

# # Update layout to set width and height
# fig.update_layout(
#     title='Carbon Emission',
#     title_x=0.5,  # Center the title
#     xaxis_title='Time',
#     yaxis_title='Carbon',
#     width=1200,  # Set width to 50%
#     height=500,  # Set height to 50%
#     margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins to make space for the paragraph on the right
# )

# Save the plot as an HTML file
html_file = 'trend_plot.html'

# Append HTML content to the HTML file

# Append HTML content to the HTML file

description1 = "We want software to become part of the climate solution, rather than be part of the climate problem. This is why we are focusing on reducing the negative impacts of software on our climate by reducing the carbon emissions that software is responsible for emitting."

description2 = "Software can also be an enabler of climate solutions. Software can be built to help accelerate decarbonization across all sectors in industry and society. We need people and organizations to focus on both aspects: of making green software and green-enabling software. But our primary focus is on creating an ecosystem for developing green software."

description3 = "The Green Software Foundation is a non-profit and has been created for the people who are in the business of building software. We are tasked with giving them answers about what they can do to reduce the software emissions they are responsible for"
    
summary = "This is a summary of the carbon emission trend. The zoom meeting is from " + str(min_timestamp) + " to " + str(min_timestamp) + ". The carbon emission trend shows an increase in carbon emissions over time. The number of CPU cores used for the analysis is " + str(num_cores_os) + ". The total energy consumed during the meeting is " + str(total_energy) + "."

machine_info = "You machine has Processor: " + processor_info + " Architecture: " + architecture[0] + " " + architecture[1]

with open(html_file, 'w') as f:
    f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
    
    f.write('<div style="width: 70%;">')  # Left side for the plot
    f.write(fig.to_html(include_plotlyjs='cdn'))  # Plotly graph
    f.write('</div>')  # End of left div
    
    f.write('<div style="width: 25%;">')  # Right side for the paragraph
    f.write('<p style="margin-top: 50px;">' + description1 + description2 + description3 + '</p>')  # Description paragraph
    f.write('</div>')  # End of right div
    f.write('</div>')  # End of flex div
############
    f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
    
    f.write('<div style="width: 70%;">')  # Left side for the plot    
    f.write('<p style="margin-top: 20px;">' + summary + '</p>')  # Description paragraph adjusted 50px lower
    f.write('<p style="margin-top: 20px;">' + machine_info +'</p>')  # Description paragraph
    f.write('<p style="margin-top: 20px;"> This is equivalent to: </p>')  # Description paragraph
    f.write('<div style="display: flex;">')  # Start of div for images in a row

    f.write('<div style="margin-right: 20px; text-align: center;">')  # Margin for spacing between images
    f.write('<img src=' + imagefull_path1 + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 1
    f.write('<p>Caption 1</p>')  # Caption for Image 1
    f.write('</div>')  # End of div for Image 1

    f.write('<div style="margin-right: 20px;">')  # Margin for spacing between images
    f.write('<img src=' + imagefull_path2 + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 2
    f.write('<p>Caption 2</p>')  # Caption for Image 2
    f.write('</div>')  # End of div for Image 2

    f.write('<div>')  # No margin for the last image
    f.write('<img src=' + imagefull_path3 + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 3
    f.write('<p>Caption 3</p>')  # Caption for Image 3
    f.write('</div>')  # End of div for Image 3

    f.write('</div>')  # End of div for images in a row    
    f.write('</div>')  # End of div for images in a column

       # Add another image to the lower right corner
    f.write('<div style="width: 25%;">')  # Right side for the paragraph
    f.write('<div>')  # No margin for the last image
    f.write('<img src=' + another_image_full_path + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Another image
    f.write('</div>')  # End of div for the additional image
    f.write('</div>')  # End of div for images in a column

    f.write('</div>')  # End of div for flex


# with open(html_file, 'w') as f:
#     f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
#     f.write('<div style="width: 70%;">')  # Left side for the plot
#     f.write(fig.to_html(include_plotlyjs='cdn'))  # Plotly graph
#     f.write('</div>')  # End of left div
#     f.write('<div style="width: 25%;">')  # Right side for the paragraph
#     f.write('<p style="margin-top: 50px;">This is a description of the carbon emission trend.</p>')  # Description paragraph
#     f.write('</div>')  # End of right div
#     f.write('</div>')  # End of flex div
#     f.write('<p style="margin-top: 50px;">This is a summary .....</p>')  # Description paragraph adjusted 50px lower
#     f.write('<p style="margin-top: 20px;">Number of core is ' + str(num_cores_os) +'</p>')  # Description paragraph
#     f.write('<div style="display: flex; flex-direction: column; width: 70%;">')  # Start of div for images in a column
#     f.write('<div style="display: flex;">')  # Start of div for images in a row
#     f.write('<div style="margin-right: 20px;">')  # Margin for spacing between images
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 1
#     f.write('<p>Caption 1</p>')  # Caption for Image 1
#     f.write('</div>')  # End of div for Image 1
#     f.write('<div style="margin-right: 20px;">')  # Margin for spacing between images
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 2
#     f.write('<p>Caption 2</p>')  # Caption for Image 2
#     f.write('</div>')  # End of div for Image 2
#     f.write('<div>')  # No margin for the last image
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image 3
#     f.write('<p>Caption 3</p>')  # Caption for Image 3
#     f.write('</div>')  # End of div for Image 3
#     f.write('</div>')  # End of div for images in a row
#     f.write('</div>')  # End of div for images in a column
    
# with open(html_file, 'w') as f:
#     f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
#     f.write('<div style="width: 70%;">')  # Left side for the plot
#     f.write(fig.to_html(include_plotlyjs='cdn'))  # Plotly graph
#     f.write('</div>')  # End of left div
#     f.write('<div style="width: 25%;">')  # Right side for the paragraph
#     f.write('<p style="margin-top: 50px;">This is a description of the carbon emission trend.</p>')  # Description paragraph
#     f.write('</div>')  # End of right div
#     f.write('</div>')  # End of flex div
#     f.write('<p style="margin-top: 50px;">This is a summary .....</p>')  # Description paragraph adjusted 50px lower
#     f.write('<p style="margin-top: 20px;">Number of core is ' + str(num_cores_os) +'</p>')  # Description paragraph
#     f.write('<div style="display: flex; justify-content: center;">')  # Start of div for images with flex layout
#     f.write('<div style="width: 380px; margin-top: 20px;">')  # Container for images with fixed width
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 100%;">')  # Image 1 with 100% width
#     f.write('<p>Caption 1</p>')  # Caption for Image 1
#     f.write('</div>')  # End of container for Image 1
#     f.write('<div style="width: 380px; margin-top: 20px;">')  # Container for images with fixed width
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 100%;">')  # Image 2 with 100% width
#     f.write('<p>Caption 2</p>')  # Caption for Image 2
#     f.write('</div>')  # End of container for Image 2
#     f.write('<div style="width: 380px; margin-top: 20px;">')  # Container for images with fixed width
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 100%;">')  # Image 3 with 100% width
#     f.write('<p>Caption 3</p>')  # Caption for Image 3
#     f.write('</div>')  # End of container for Image 3
#     f.write('</div>')  # End of div for images

# with open(html_file, 'w') as f:
#     f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
#     f.write('<div style="width: 70%;">')  # Left side for the plot
#     f.write(fig.to_html(include_plotlyjs='cdn'))  # Plotly graph
#     f.write('</div>')  # End of left div
#     f.write('<div style="width: 25%;">')  # Right side for the paragraph
#     f.write('<p style="margin-top: 50px;">This is a description of the carbon emission trend.</p>')  # Description paragraph
#     f.write('</div>')  # End of right div
#     f.write('</div>')  # End of flex div
#     f.write('<p style="margin-top: 50px;">This is a summary .....</p>')  # Description paragraph adjusted 50px lower
#     f.write('<p style="margin-top: 20px;">Number of core is ' + str(num_cores_os) +' </p>')  # Description paragraph
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 380px; margin-top: 20px;">')  # Image
#     f.write('</div>')  # End of div

# with open(html_file, 'w') as f:
#     f.write('<div style="display: flex; justify-content: space-between;">')  # Start of div with flex layout
#     f.write('<div style="width: 70%;">')  # Left side for the plot
#     f.write(fig.to_html(include_plotlyjs='cdn'))  # Plotly graph
#     f.write('</div>')  # End of left div
#     f.write('<div style="width: 25%;">')  # Right side for the paragraph
#     f.write('<p>This is a description of the carbon emission trend.</p>')  # Description paragraph
#     f.write('</div>')  # End of right div
#     f.write('</div>')  # End of flex div
#     f.write('<p style="margin-top: 20px;">This is a summary .....</p>')  # Description paragraph
#     f.write('<p style="margin-top: 20px;">Number of core is ' + str(num_cores_os) +' </p>')  # Description paragraph
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 500px; margin-top: 20px;">')  # Image
#     f.write('</div>')  # End of div

# Read the CSV file
# df = pd.read_csv('zoomOutput.csv')

# # Create a plotly figure
# fig = go.Figure()

# # Add a scatter plot with time as x-axis and value as y-axis
# fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cpu/energy'], mode='lines+markers'))

# # Update layout to set width and height
# fig.update_layout(
#     title='Carbon Emission',
#     xaxis_title='Time',
#     yaxis_title='Carbon',
#     width=1200,  # Set width to 50%
#     height=500  # Set height to 50%
# )

# # Save the plot as an HTML file
# html_file = 'trend_plot.html'
# # fig.write_html(html_file)


# # Append HTML content to the HTML file
# with open(html_file, 'a') as f:
#     f.write('<div style="width: 100%; text-align: center;">')  # Start of div
#     f.write(fig.to_html(include_plotlyjs='cdn'))  # Plotly graph
#     f.write('<p style="margin-top: 20px;">This is a description of the carbon emission trend.</p>')  # Description paragraph
#     f.write('<p style="margin-top: 20px;">Number of core is ' + str(num_cores_os) +' </p>')  # Description paragraph
#     f.write('<img src=' + imagefull_path + ' alt="Image" style="width: 500px; margin-top: 20px;">')  # Image
#     f.write('</div>')  # End of div

# Get the current working directory
current_directory = os.getcwd()
full_path = os.path.join(current_directory, html_file)

# Open the HTML file in a web browser
webbrowser.open('file://' + full_path)


