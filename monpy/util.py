import psutil
import json

temps = psutil.sensors_temperatures()
print(temps["coretemp"][0].current)
