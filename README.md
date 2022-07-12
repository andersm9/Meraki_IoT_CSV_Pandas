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

### ORG_ID
The Meraki ORG_ID uniquely identifies an organization assoiated with an API key (AN API key may have multiple organizations). The ORG_ID can be obtained by making a "GET Organizations" call to the meraki Dashboard API, such as from the Meraki [Documentation](https://developer.cisco.com/meraki/api-v1/#!get-organizations)

## Output

An example output CSV file is provided below, which is printed to 'results.scv' in the same directory as the script is run in. This provides a header row with each sensor & metric combination, and an individual timestamped row for each sampleTime:
| Timestamp      | Q9EB_M7KP_VLA3_humidity |Q9EB_M7KP_VLA3_temperature| Q5MS_ISB7_PS83_water|
| ----------- | ----------- | ----------- | ----------- |
| 1657538255.0   | 59       |22.0|FALSE|
| 1657538755.0 |59       |22.1|FALSE|
|1657539255.0 | 60|22.2|FALSE|
