mport RPi.GPIO as GPIO
import Adafruit_DHT
import mysql.connector
import time
import datetime

# MySQL-Verbindung
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="raspberry",
  database="sensordaten"
)

# DHT22-Sensoren
dht = Adafruit_DHT.DHT22
sensoren = {
    "oben": 16,
    "unten": 17,
    "aussen": 18
}

def lese_sensor(sensor_id, pin):
    humidity, temperature = Adafruit_DHT.read_retry(dht, pin)
    if humidity is not None and temperature is not None:
        return temperature, humidity
    else:
        print(f"Fehler beim Lesen von Sensor {sensor_id}")
        return None, None

def speichere_daten(sensor_id, temperatur, feuchtigkeit):
    if temperatur is None or feuchtigkeit is None:
        return

    mycursor = mydb.cursor()
    sql = "INSERT INTO dht22 (sensor_id, time, Temp, Rf) VALUES (%s, %s, %s, %s)"
    val = (sensor_id, datetime.datetime.now(), temperatur, feuchtigkeit)
    mycursor.execute(sql, val)
    mydb.commit()

try:
    while True:
        for sensor_id, pin in sensoren.items():
            temperatur, feuchtigkeit = lese_sensor(sensor_id, pin)
            if temperatur is not None and feuchtigkeit is not None:
                print(f"{sensor_id}: Temp = {temperatur:.1f} °C, Feuchtigkeit = {feuchtigkeit:.1f} %")
                speichere_daten(sensor_id, temperatur, feuchtigkeit)
            else:
                print(f"Daten für Sensor {sensor_id} konnten nicht gelesen werden.")

        time.sleep(120)  # Alle 2 Minuten

except KeyboardInterrupt:
    print("Skript beendet.")

finally:
    mydb.close()
    GPIO.cleanup()
