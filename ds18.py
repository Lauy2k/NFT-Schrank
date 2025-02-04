import os
import glob
import time
import datetime
import mysql.connector

# MySQL-Verbindung
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="raspberry",
    database="sensordaten"
)

# One-Wire-Konfiguration
os.system('modprobe w1-gpio')  # Aktiviert die One-Wire-Unterstützung
os.system('modprobe w1-therm') # Aktiviert das Modul für DS18B20

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]  # Sucht nach dem Geräteordner des DS18B20
device_file = device_folder + '/w1_slave'

def lese_temperatur():
    lines = lese_datei(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = lese_datei(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def lese_datei(file):
    with open(file, 'r') as f:
        return f.readlines()

def schreibe_daten(temperatur):
    mycursor = mydb.cursor()
    try:
        now = datetime.datetime.now()
        sql = "INSERT INTO ds18 (timestamp, temp) VALUES (%s, %s)"
        val = (now, temperatur)
        mycursor.execute(sql, val)
        mydb.commit()
        print(f"Temperatur in Datenbank geschrieben: {now}, {temperatur:.2f}°C")
    except mysql.connector.Error as err:
        print(f"Fehler beim Schreiben in die Datenbank: {err}")
    finally:
        mycursor.close()

try:
    while True:
        temperatur = lese_temperatur()
        if temperatur is not None:
            schreibe_daten(temperatur)
        time.sleep(60)  # Daten alle 60 Sekunden schreiben

except KeyboardInterrupt:
    print("Skript beendet.")

finally:
    mydb.close()
