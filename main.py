# Hauptdatei die Skripte aufruft und Logik des Systems Steueret 
import time
import sensoren
import datenlogger

def main():
    """Hauptfunktion des Programms."""

    while True:
        # Lese die Sensordaten aus
        sensor_data = sensoren.get_sensor_data()

        # Schreibe die Daten in die CSV-Datei
        datenlogger.log_sensor_data(sensor_data)

        # Warte 10 Minuten
        time.sleep(600)

if __name__ == "__main__":
    main()
