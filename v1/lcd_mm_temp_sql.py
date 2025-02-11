import smbus
import time
from w1thermsensor import W1ThermSensor
import mysql.connector
import sys
import os

# Pfad zum Modul hinzufügen
sys.path.append('/home/Pi/DFRobot_RaspberryPi_A02YYUW')
from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance as Board

# --- Konfiguration des LCD-Displays ---
I2C_ADDR = 0x27  # I2C-Adresse des LCD-Displays (kann je nach Modell variieren)
LCD_WIDTH = 16   # Maximale Anzahl der Zeichen pro Zeile des Displays

# --- Befehle für das LCD-Display ---
LCD_CHR = 1  # Modus: Zeichen senden
LCD_CMD = 0  # Modus: Befehl senden

LCD_LINE_1 = 0x80  # LCD RAM Adresse für die 1. Zeile
LCD_LINE_2 = 0xC0  # LCD RAM Adresse für die 2. Zeile

LCD_BACKLIGHT = 0x08  # Hintergrundbeleuchtung: Ein: 0x08, Aus: 0x00

ENABLE = 0b00000100  # Aktiviert den Eingang des LCD-Displays

# --- Timing-Konstanten für die Ansteuerung des LCD-Displays ---
E_PULSE = 0.0005  # Pulslänge für das Enable-Signal (in Sekunden)
E_DELAY = 0.0005  # Verzögerung nach dem Enable-Signal (in Sekunden)

# --- I2C-Objekt erstellen ---
bus = smbus.SMBus(1)  # Busnummer kann je nach System variieren (0 oder 1)

# --- Funktion zur Initialisierung des LCD-Displays ---
def lcd_init():
    # Initialisierungssequenz für das LCD-Display
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialisierung
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialisierung
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor inkrement
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display ein, Cursor aus
    lcd_byte(0x28, LCD_CMD)  # 101000 Datenlänge, Zeilen, Zeichensatz
    lcd_byte(0x01, LCD_CMD)  # 000001 Display löschen
    time.sleep(E_DELAY)  # Kurze Verzögerung nach der Initialisierung

# --- Funktion zum Senden eines Bytes an das LCD-Display ---
def lcd_byte(bits, mode):
    # Sendet Byte an die Datenpins
    # bits = Daten
    # mode = 1 für Zeichen, 0 für Befehl

    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT  # High-Nibble mit Hintergrundbeleuchtung
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT  # Low-Nibble mit Hintergrundbeleuchtung

    # High Bits senden
    bus.write_byte(I2C_ADDR, bits_high)  # Byte an das LCD senden
    lcd_toggle_enable(bits_high)  # Enable-Signal umschalten

    # Low Bits senden
    bus.write_byte(I2C_ADDR, bits_low)  # Byte an das LCD senden
    lcd_toggle_enable(bits_low)  # Enable-Signal umschalten

# --- Funktion zum Umschalten des Enable-Bits ---
def lcd_toggle_enable(bits):
    # Schaltet das Enable-Bit ein und aus, um Daten zu schreiben
    time.sleep(E_DELAY)  # Kurze Verzögerung
    bus.write_byte(I2C_ADDR, (bits | ENABLE))  # Enable-Bit setzen
    time.sleep(E_PULSE)  # Kurzer Puls
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))  # Enable-Bit zurücksetzen
    time.sleep(E_DELAY)  # Kurze Verzögerung

# --- Funktion zum Anzeigen einer Zeichenkette auf dem LCD-Display ---
def lcd_string(message, line):
    # Sendet eine Zeichenkette an das Display
    message = message.ljust(LCD_WIDTH, " ")  # Nachricht mit Leerzeichen auffüllen

    lcd_byte(line, LCD_CMD)  # Zeile auswählen

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)  # Zeichen für Zeichen senden

# --- Konfiguration der Datenbankverbindung ---
mydb = mysql.connector.connect(
    host="localhost",  # Hostname des MySQL-Servers
    user="root",  # Benutzername für die Datenbank
    password="raspberry",  # Passwort für die Datenbank
    database="sensordaten"  # Name der Datenbank
)

# --- Initialisierung des Ultraschallsensors ---
board = Board()
dis_min = 0   # Minimum ranging threshold: 0mm
dis_max = 4500 # Highest ranging threshold: 4500mm
board.set_dis_range(dis_min, dis_max)

# --- Hauptfunktion ---
def main():
    # Initialisierung des LCD-Displays
    lcd_init()

    # Initialisierung des Temperatursensors
    sensor = W1ThermSensor()

    last_db_write = 0  # Variable zum Speichern des letzten Schreibzeitpunkts in die Datenbank

    while True:  # Endlosschleife
        # Temperatur vom Sensor lesen
        temperature = sensor.get_temperature()

        # Distanz vom Sensor lesen
        distance = board.getDistance()

        # Temperatur auf dem LCD anzeigen (erste Zeile)
        lcd_string("Temp: {:.2f} C".format(temperature), LCD_LINE_1)  

        # Distanz auf dem LCD anzeigen (zweite Zeile) mit 4 Stellen
        lcd_string("Dist: {:4d} mm".format(distance), LCD_LINE_2)  

        # Temperatur in der Datenbank speichern (alle 30 Sekunden)
        current_time = time.time()
        if current_time - last_db_write >= 30:
            try:
                cursor = mydb.cursor()  # Cursor erstellen
                sql = "INSERT INTO temperatur (temperatur) VALUES (%s)"  # SQL-Abfrage
                val = (temperature,)  # Wert für die Abfrage
                cursor.execute(sql, val)  # Abfrage ausführen
                mydb.commit()  # Änderungen speichern
                print(cursor.rowcount, "Datensatz eingefügt.")  # Bestätigung ausgeben
                last_db_write = current_time  # Letzten Schreibzeitpunkt aktualisieren
            except mysql.connector.Error as err:
                print("Fehler beim Schreiben in die Datenbank:", err)  # Fehlermeldung ausgeben

        # Kurze Pause, um die CPU zu entlasten (z.B. 5 Sekunden)
        time.sleep(5)


if __name__ == '__main__':
    try:
        main()  # Hauptfunktion ausführen
    except KeyboardInterrupt:
        pass  # Programm beenden bei Tastaturunterbrechung (Strg+C)
    finally:
        lcd_byte(0x01, LCD_CMD)  # Display löschen
        lcd_string("Goodbye!", LCD_LINE_1)  # Abschiedsnachricht anzeigen
