import requests
import os
import json
from pprint import pprint
import time
import csv
from datetime import datetime
import math
import meraki


def get_data(lookback):
    #retrieve the historic sensor data from Meraki
    url = "https://api.meraki.com/api/v1/organizations/265528/sensor/readings/history" + "?timespan=604800"
    payload = None
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Cisco-Meraki-API-Key": "84ff64ae344684bd483875c613c77b997cbe0489"
    }

    response = dashboard.sensor.getOrganizationSensorReadingsHistory(265528,total_pages='all',timespan=lookback)
    print(type(response))
    return(response)


def get_headers(response):
    #define the column headers from the sensor data
    serials = set()
    for datapoint in response:
        if 'serial' in datapoint:
            if 'temperature' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_temperature")
            if 'humidity' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_humidity")
            if 'indoorAirQuality' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_indoorAirQuality")
            if 'tvoc' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_tvoc")
            if 'pm25' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_pm25")
            if 'door' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_door")
            if 'noise' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_noise")
            if 'water' in datapoint:
                serials.add(datapoint['serial'].replace("-", "_") + "_water")
            else:
                continue

    # alter the format of the serial number
    print(serials)
    return(serials)

def convert_timestamps(response):
    #convert zulu time to epoch/unix time
    for datapoint in response:
        Zulu_timestamp = datapoint['ts']

        Epoch_timestamp = time.strptime(Zulu_timestamp, "%Y-%m-%dT%H:%M:%SZ")

        unix_time_local = time.mktime(Epoch_timestamp)

        datapoint['ts'] = unix_time_local
    return(response)

def timeSpan(unixResponse):
    #define the start and end times (in epoch/unix time) of the sample data
    startTime = 9999999999
    endTime = 0
    for datapoint in unixResponse:
        if datapoint['ts'] < startTime:
            startTime = datapoint['ts']
        if datapoint['ts'] > endTime:
            endTime = datapoint['ts']
    return(startTime, endTime)

def timeSteps(unixResponse, startTime, endTime, sampleTime):
    # define each time step within the start and end times of the sensor data
    iterateStartTime = startTime
    iterateEndTime = iterateStartTime + sampleTime
    ###timeSteps is the number of times we iterate over a time range, whole number
    timeSteps = (endTime - startTime)/sampleTime

    IntTimesteps = math.ceil(timeSteps)
    steps = []
    n = 0

    #while loop iterates over the data, once for each of the steps
    while n < IntTimesteps:

        stepStart = startTime + n*sampleTime
        stepStop = stepStart + sampleTime
        #MAKE CALL HERE TO GO THROUGH UNIXRESPONSE AND LOOK FOR THE RELEVANT TIMESTAMPS
        n = n+ 1
        iterateData(unixResponse, stepStart, stepStop, n)





def iterateData(unixResponse, iterateStartTime, iterateEndTime, n):
    #iterate through the sensor data in a given timeStep to define the latest datapoint for each column
    loopStart = startTime

    for datapoint in unixResponse:

        #iterates over the entire dataset, able to select datapoints that are between the start and end times
        if datapoint['ts'] > iterateStartTime and datapoint['ts']< iterateEndTime:
            print("---------------------")
            pprint(datapoint)
            #iterate through the datapoints in a given timerange, looking for specific keys/value pairs
            for reading in header_list:
                #split out the serial and reading
                #print(reading)
                split_reading = reading.split("_")
                print("split_reading")
                print(split_reading)

                # check if the datapoint serial number is the same as the current serial number
                if split_reading[0] in datapoint['serial']:
                    print(f"found serial {datapoint['serial']}")

                    print('in split 0')
                    if split_reading[3] in datapoint:
                        # check if the datapoint reading is the same as the current reading
                        print("in split 1")

                        #ADD IN THE DATAPOINT INTO THE RELEVANT COLUMN (OVERWRITE IF NECESARY
                        if 'temperature' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['temperature']['celsius']
                            continue
                        elif 'humidity' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['humidity']['relativePercentage']
                            continue
                        elif 'indoorAirQuality' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['indoorAirQuality']['score']
                            continue
                        elif 'tvoc' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['tvoc']['concentration']
                            continue
                        elif 'pm25' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['pm25']['concentration']
                            continue
                        elif 'door' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['door']['open']
                            continue
                        elif 'noise' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['noise']['ambient']['level']
                            continue
                        elif 'water' in datapoint:
                            last_result[header_list.index(reading)] = datapoint['water']['present']
                            continue

        loopStart = loopStart + sampleTime
    last_result[0] = iterateEndTime
    print("last_result:")
    print(f"{last_result}")
    with open('results.csv', 'a') as f:
        write = csv.writer(f)
        write.writerow(last_result)



def initialLine():
    for entry in header_list:
        last_result.append(0)
    #print(last_result)




if __name__ == "__main__":
    #define the 'lookback' timespan in seconds
    lookback = 6000
    #sample time in seconds
    sampleTime = 500
    #API Key here (this is an example key only):
    API_Key = "4gfh6tjs94bsmg1d486875c653c67b997cbekro4b"

    dashboard = meraki.DashboardAPI(API_Key)
    last_result = []
    next_result = []
    response = get_data(lookback)

    try:
        headers = get_headers(response)
        header_list = list(headers)
        #order the list alphanumerically for consistency when run multiple times
        header_list = sorted(header_list, key=lambda item: (int(item.partition(' ')[0])
                                           if item[0].isdigit() else float('inf'), item))
        print(header_list)
        header_list.insert(0,"Timestamp")

        #Write the header to the csv file
        with open('results.csv', 'w') as f:
            write = csv.writer(f)
            write.writerow(header_list)


    except Exception as e: 
        print(e)
        time.sleep(10)
        pass
    unixResponse = convert_timestamps(response)

    # print the data to a local file - DON"T KNOW WHAT THIS IS FOR????
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(unixResponse, f, ensure_ascii=False, indent=4)
    startTime, endTime = timeSpan(unixResponse)
    timeSpan = endTime - startTime

    print(f"startTime = {startTime}")
    print(f"endTime= {endTime}")
    initialLine()
    timeSteps(unixResponse, startTime, endTime, sampleTime)
