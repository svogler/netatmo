#!/usr/bin/python3
# encoding=utf-8

import time
import lnetatmo
import datetime
from influxdb import InfluxDBClient

host = '192.168.178.22'
port = '8086'
user = 'admin'
password = 'influx'
dbname = 'netatmo'

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

#json_body = [{'measurement': 'netatmo', 'time': datetime.datetime(2023, 11, 8, 20, 43, 43, 10371), 'fields': {'Innen.Temperature': 22.4, 'Innen.CO2': 861.0, 'Innen.Humidity': 56.0, 'Innen.Noise': 35.0, 'Innen.Pressure': 1008.2, 'Innen.AbsolutePressure': 979.5, 'Innen.min_temp': 22.2, 'Innen.max_temp': 23.2, 'Innen.date_max_temp': 1699448009, 'Innen.date_min_temp': 1699411891, 'Innen.temp_trend': 'stable', 'Innen.pressure_trend': 'down', 'Innen.When': '21:38:28', 'Innen.wifi_status': 67.0, 'Außen.Temperature': 8.3, 'Außen.Humidity': 80.0, 'Außen.min_temp': 7.1, 'Außen.max_temp': 10.7, 'Außen.date_max_temp': 1699445886, 'Außen.date_min_temp': 1699471008, 'Außen.temp_trend': 'up', 'Außen.When': '21:37:58', 'Außen.battery_vp': 5470.0, 'Außen.battery_percent': 71.0, 'Außen.rf_status': 64.0, 'Regen.Rain': 0.0, 'Regen.sum_rain_1': 0.0, 'Regen.sum_rain_24': 0.1, 'Regen.When': '21:38:24', 'Regen.battery_vp': 4976.0, 'Regen.battery_percent': 53.0, 'Regen.rf_status': 68.0}}]
#print(json_body)

dbclient.write_points(json_body)

