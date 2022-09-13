"""
Script to converst Meraki Sensor Data from JSON format to CSV
"""

import time
import csv
import math
import meraki
import pandas as pd
import matplotlib.pyplot as plt





def get_data():
    """
    acquire sensor data in JSON format from the Meraki Dashboard API
    """

    dash_response = DASHBOARD.sensor.getOrganizationSensorReadingsHistory(ORG_ID, total_pages='all', timespan=LOOKBACK,suppress_logging=True)
    return dash_response

def get_headers():
    """
    define the column HEADERS from the sensor data
    """

    serials = set()
    for datapoint in RESPONSE:
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

    return serials

def convert_timestamps(response):
    """
    #convert zulu time to epoch/unix time 
    """
    for datapoint in response:
        zulu_timestamp = datapoint['ts']

        epoch_timestamp = time.strptime(zulu_timestamp, "%Y-%m-%dT%H:%M:%SZ")

        unix_time_local = time.mktime(epoch_timestamp)

        datapoint['ts'] = unix_time_local
    return response

def time_span(unix_response):
    """
    define the start and end times (in epoch/unix time) of the entire sample data
    """

    start_time = 9999999999
    end_time = 0
    for datapoint in unix_response:
        if datapoint['ts'] < start_time:
            start_time = datapoint['ts']
        if datapoint['ts'] > end_time:
            end_time = datapoint['ts']
    return start_time, end_time

def time_steps(start_time, sample_time, unix_response, end_time):
    """
    # define each time step within the start and end times of the sensor data 
    """
    ###time_steps is the number of times we iterate over a time range, whole number
    no_time_steps = (end_time - start_time)/sample_time
    int_time_steps = math.ceil(no_time_steps)
    n = 0

    #while loop iterates over the data, once for each of the steps
    while n < int_time_steps:

        step_start = start_time + n*sample_time
        step_stop = step_start + sample_time
        #MAKE CALL HERE TO GO THROUGH UNIXRESPONSE AND LOOK FOR THE RELEVANT TIMESTAMPS
        n = n+ 1
        iterate_data(unix_response, step_start, step_stop)

def iterate_data(unix_response, iterate_start_tme, iterateEndTime):
    """
    iterate through the sensor data in a given timeStep to define the latest datapoint for each column
    """

    loop_start = START_TIME

    for datapoint in unix_response:

        #iterates over the entire dataset, able to select datapoints that are between the start and end times
        if datapoint['ts'] > iterate_start_tme and datapoint['ts'] < iterateEndTime:
            #iterate through the datapoints in a given timerange, looking for specific keys/value pairs
            for reading in HEADER_LIST:
                #split out the serial and reading
                split_reading = reading.split("_")

                # check if the datapoint serial number is the same as the current serial number
                if split_reading[0] in datapoint['serial']:
                    if split_reading[1] in datapoint['serial']:
                        if split_reading[2] in datapoint['serial']:
                            # check if the datapoint reading is the same as the current reading
                            if split_reading[3] in datapoint:
                            #ADD IN THE DATAPOINT INTO THE RELEVANT COLUMN (OVERWRITE IF NECESARY
                                if 'temperature' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['temperature']['celsius']
                                    continue
                                if 'humidity' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['humidity']['relativePercentage']
                                    continue
                                elif 'indoorAirQuality' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['indoorAirQuality']['score']
                                    continue
                                elif 'tvoc' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['tvoc']['concentration']
                                    continue
                                elif 'pm25' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['pm25']['concentration']
                                    continue
                                elif 'door' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['door']['open']
                                    continue
                                elif 'noise' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['noise']['ambient']['level']
                                    continue
                                elif 'water' in datapoint:
                                    LAST_RESULT[HEADER_LIST.index(reading)] = datapoint['water']['present']
                                    continue
        loop_start = loop_start + SAMPLE_TIME
    LAST_RESULT[0] = iterateEndTime
    with open('results.csv', 'a') as f:
        write = csv.writer(f)
        write.writerow(LAST_RESULT)
        ## write a row here using LAST_RESULT
        global df
        df.loc[len(df)] = LAST_RESULT


if __name__ == "__main__":

    x = 1
    #define the 'LOOKBACK' timespan in seconds
    LOOKBACK = 300000
    #sample time in seconds
    SAMPLE_TIME = 500
    #API Key here:
    API_KEY = ""
    # e.g. API_KEY = "9jhdf83sbfu39275hdbsk49fn8nd10fbhs93bn"
    ORG_ID = ""
    # e.g. ORG_ID = "123456"

    DASHBOARD = meraki.DashboardAPI(API_KEY)
    LAST_RESULT = []
    NEXT_RESULT = []
    RESPONSE = get_data()

    try:
        HEADERS = get_headers()
        HEADER_LIST = list(HEADERS)
        #order the list alphanumerically for consistency when run multiple times
        HEADER_LIST = sorted(HEADER_LIST, key=lambda item: (int(item.partition(' ')[0])
        if item[0].isdigit() else float('inf'), item))
        HEADER_LIST.insert(0, "Timestamp")
        #df = pd.DataFrame(HEADER_LIST)
        df = pd.DataFrame(columns=HEADER_LIST)
        #Write the header to the csv file
        with open('results.csv', 'w') as f:
            write = csv.writer(f)
            write.writerow(HEADER_LIST)

    except Exception as e:
        print(e)
        time.sleep(10)

    UNIX_RESPONSE = convert_timestamps(RESPONSE)
    START_TIME, END_TIME = time_span(UNIX_RESPONSE)
    TIME_SPAN = END_TIME - START_TIME
    for entry in HEADER_LIST:
        #define an initial data row, populated with all zeros
        LAST_RESULT.append(0)
    time_steps(START_TIME, SAMPLE_TIME, UNIX_RESPONSE, END_TIME)
    print("final result")
    print(df)
    #df.plot()
    #plt.plot(df['Q3CA_6TWV_UXCS_humidity'], df['Q3CA_6TWV_UXCS_temperature'], color='g', label='')
    for col in df.columns:
        if not col == 'Timestamp':
            plt.plot(df['Timestamp'], df[col], label='Line ' + col)
    plt.yscale('log')
    plt.legend(fontsize=8)
    #plt.legend()
    plt.show()
