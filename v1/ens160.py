from __future__ import print_function
import sys
import os
import time
import datetime
import mysql.connector

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from DFRobot_ENS160 import *

# Sensor initialisieren (I2C oder SPI, wie in deinem Originalcode)
sensor = DFRobot_ENS160_I2C(i2c_addr=0x53, bus=1)  # Beispiel: I2C

# MySQL-Verbindung (als Funktion)
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="raspberry",  # Ändere dies in dein echtes Passwort!
            database="sensordaten"
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def schreibe_daten(aqi, tvoc, eco2):
    mydb = connect_to_db()
    if mydb is None:
        return

    mycursor = mydb.cursor()
    try:
        now = datetime.datetime.now()  # Aktuelles Datum und Uhrzeit
        sql = "INSERT INTO AirQ (timestamp, aqi, tvoc, eCO2) VALUES (%s, %s, %s, %s)"
        val = (now, aqi, tvoc, eco2)
        mycursor.execute(sql, val)
        mydb.commit()
        print(f"Daten in AirQ geschrieben: {now}, AQI: {aqi}, TVOC: {tvoc}, eCO2: {eco2}")
    except mysql.connector.Error as err:
        print(f"Fehler beim Schreiben in die Datenbank: {err}")
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()

def get_calibration_data():
    mydb = connect_to_db()
    if mydb is None:
        return None, None

    mycursor = mydb.cursor()
    try:
        sql = "SELECT temp, rf FROM dht22_oben ORDER BY timestamp DESC LIMIT 1" # Neueste Werte zuerst
        mycursor.execute(sql)
        result = mycursor.fetchone()
        if result:
            temp, rf = result
            print(f"Kalibrierungsdaten aus der Datenbank: Temperatur={temp}, Luftfeuchtigkeit={rf}")
            return temp, rf
        else:
            print("Keine Kalibrierungsdaten in der Datenbank gefunden.")
            return None, None
    except mysql.connector.Error as err:
        print(f"Fehler beim Lesen aus der Datenbank: {err}")
        return None, None
    finally:
        if mycursor:
            mycursor.close()
        if mydb:
            mydb.close()

def setup():
    while (sensor.begin() == False):
        print('Please check that the device is properly connected')
        time.sleep(3)
    print("sensor begin successfully!!!")

    sensor.set_PWR_mode(ENS160_STANDARD_MODE)
    temp, rf = get_calibration_data() # Kalibrierungsdaten aus der DB holen

    if temp is not None and rf is not None:
        sensor.set_temp_and_hum(ambient_temp=temp, relative_humidity=rf)  # Mit Werten aus DB kalibrieren
    else:
        sensor.set_temp_and_hum(ambient_temp=25.00, relative_humidity=50.00) # Default-Werte, falls keine in DB

def loop():
    sensor_status = sensor.get_ENS160_status()
    print("Sensor operating status : %u" % sensor_status)  # Überprüfe den Status!

    aqi = sensor.get_AQI
    tvoc = sensor.get_TVOC_ppb
    eco2 = sensor.get_ECO2_ppm

    print("Air quality index : %u" % aqi)
    print("Concentration of total volatile organic compounds : %u ppb" % tvoc)
    print("Carbon dioxide equivalent concentration : %u ppm" % eco2)

    schreibe_daten(aqi, tvoc, eco2) # Daten in die Datenbank schreiben

    print()
    time.sleep(0.5)  # Anpassen nach Bedarf

if __name__ == "__main__":
    setup()
    while True:
        loop()
