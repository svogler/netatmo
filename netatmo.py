#!/usr/bin/python3
# encoding=utf-8

import time
import lnetatmo
import datetime
from influxdb import InfluxDBClient

host = 'host'
port = 'port'
user = 'admin'
password = 'password'
dbname = 'database'

utctime = datetime.datetime.utcnow()
authorization = lnetatmo.ClientAuth()
weather = lnetatmo.WeatherStationData(authorization)

user = weather.user

print("Station owner : ", user.mail)
print("Data units    : ", user.unit)

json_values = {}


# For each station in the account
for station in weather.stations:

    print("\nSTATION : %s\n" % weather.stations[station]["station_name"])

    # For each available module in the returned data of the specified station
    # that should not be older than one hour (3600 s) from now
    for module, moduleData in weather.lastData(station=station, exclude=3600).items() :
       
        # Name of the module (or station embedded module)
        # You setup this name in the web netatmo account station management
        print(module)
        
        # List key/values pair of sensor information (eg Humidity, Temperature, etc...)
        for sensor, value in moduleData.items() :
            # To ease reading, print measurement event in readable text (hh:mm:ss)
            if sensor == "When" : value = time.strftime("%H:%M:%S",time.localtime(value))
            print("%30s : %s" % (module + "." + sensor, value))

            # convert to float to avoid type conflicts on influxdb
            if isinstance(value, int) : value = float(value)
            json_values[module + "." + sensor] = value

dbclient = InfluxDBClient(host, port, user, password, dbname)

json_body = [
{
    "measurement": "netatmo",
    "time": utctime,
    "fields": json_values
}
]

#print(json_body)

dbclient.write_points(json_body)

