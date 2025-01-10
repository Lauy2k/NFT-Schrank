import csv
from datetime import datetime

def log_sensor_data(sensor_data):
    """Schreibt die Sensordaten in die CSV-Datei."""

    # Erstelle ein Dictionary mit den Sensordaten und dem aktuellen Zeitstempel
    data = {
        "timestamp": datetime.now().isoformat(),
        "DHT22Oben_temperature": sensor_data["DHT22Oben"]["temperature"],
        "DHT22Oben_humidity": sensor_data["DHT22Oben"]["humidity"],
        "DHT22Unten_temperature": sensor_data["DHT22Unten"]["temperature"],
        "DHT22Unten_humidity": sensor_data["DHT22Unten"]["humidity"],
        "DHT22Aussen_temperature": sensor_data["DHT22Aussen"]["temperature"],
        "DHT22Aussen_humidity": sensor_data["DHT22Aussen"]["humidity"],
    }

    # Schreibe die Daten in die CSV-Datei
    with open('sensordaten.csv', 'a', newline='') as csvfile:
        fieldnames = data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow(data)
