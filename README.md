# Meraki_IoT_CSV
## Usage
This tool allows for the conversion of Meraki Sensor data from the natove JSON encoding format to a Comma Seperated Vsariable (CSV) format.  
Many tools such as Machine Learning algorithms use CSV format as the imput against which to train and test models

The tool is launched by the following command:  
> python Meraki_IoT_CSV.py    

or for Mac:  
> python3 Meraki_IoT_CSV.py 


## Output
The tool automatically detaects the available MT sensors and their associated Metrics and delivers the values in the form of a time orders CSV file.  

## Paramaters
The following parameters are required to be configured (examples are provided in the provided code.

### loopback
The 'loopback' value defines a timespan  which will be used to gather data over. For instance a value of 600000 will provide a value of approximately one week

### sampleTime
The 'sampleTime' value defines the ganularity with which data is output to CSV. For instance a value of 500 means that a line of sensor reading will be provided for every 500 period. In the event that an individual sensor has not provided a reading in this timespan, the previous reading will be used. In the event that multiple readings have been provided in this timesapn, the most recent reading will be used.

### Meraki Dashboard API key
The Meraki Dashboard API key is available as described [here](https://documentation.meraki.com/General_Administration/Other_Topics/Cisco_Meraki_Dashboard_API)
