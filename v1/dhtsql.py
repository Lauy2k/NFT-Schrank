import RPi.GPIO as GPIO
import Adafruit_DHT
import mysql.connector
import time
import datetime

# MySQL-Verbindung (als Funktion)
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="raspberry",
        database="sensordaten"
    )

# DHT22-Sensoren und Tabellen
dht = Adafruit_DHT.DHT22
sensoren = {
    "oben": {"pin": 16, "tabelle": "dht22_oben"},
    "unten": {"pin": 17, "tabelle": "dht22_unten"},
    "aussen": {"pin": 18, "tabelle": "dht22_aussen"}
}

def lese_sensor(sensor_id, pin):
    humidity, temperature = Adafruit_DHT.read_retry(dht, pin)
    if humidity is not None and temperature is not None:
        return temperature, humidity
    else:
        print(f"Fehler beim Lesen von Sensor {sensor_id}")
        return None, None

def speichere_daten(tabelle, temperatur, feuchtigkeit):
    mydb = connect_to_db()  # Verbindung innerhalb der Funktion herstellen
    if mydb is None:
        print("Keine Verbindung zur Datenbank möglich.")
        return

    mycursor = mydb.cursor()
    try:
        now = datetime.datetime.now()
        sql = f"INSERT INTO {tabelle} (timestamp, temp, rf) VALUES (%s, %s, %s)"  # f-string verwenden
        val = (now, temperatur, feuchtigkeit)
        mycursor.execute(sql, val)
        mydb.commit()
        print(f"Daten für Sensor in Tabelle {tabelle} gespeichert: {now}, {temperatur:.1f}°C, {feuchtigkeit:.1f}%")
    except mysql.connector.Error as err:
        print(f"Fehler beim Schreiben in Tabelle {tabelle}: {err}")
    finally:
        mycursor.close()
        mydb.close()  # Verbindung immer schließen

try:
    while True:
        for sensor_id, details in sensoren.items():
            temperatur, feuchtigkeit = lese_sensor(sensor_id, details["pin"])
            if temperatur is not None and feuchtigkeit is not None:
                print(f"{sensor_id}: Temp = {temperatur:.1f} °C, Feuchtigkeit = {feuchtigkeit:.1f} %")
                speichere_daten(details["tabelle"], temperatur, feuchtigkeit)
            else:
                print(f"Daten für Sensor {sensor_id} konnten nicht gelesen werden.")

        time.sleep(120)  # Alle 2 Minuten

except KeyboardInterrupt:
    print("Skript beendet.")

finally:
    GPIO.cleanup()
