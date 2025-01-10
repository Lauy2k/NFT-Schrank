import Adafruit_DHT

# Definiere die GPIO-Pins, an die die Sensoren angeschlossen sind
DHT_PIN_OBEN = 16
DHT_PIN_UNTEN = 17
DHT_PIN_AUSSEN = 18

# Definiere den Sensortyp (DHT22)
DHT_SENSOR = Adafruit_DHT.DHT22

def get_sensor_data():
  """Liest die Temperatur und Luftfeuchtigkeit von allen Sensoren aus."""

  humidity_oben, temperature_oben = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN_OBEN)
  humidity_unten, temperature_unten = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN_UNTEN)
  humidity_aussen, temperature_aussen = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN_AUSSEN)

  # Gib die Messwerte als Dictionary zurück
  return {
      "DHT22Oben": {"temperature": temperature_oben, "humidity": humidity_oben},
      "DHT22Unten": {"temperature": temperature_unten, "humidity": humidity_unten},
      "DHT22Aussen": {"temperature": temperature_aussen, "humidity": humidity_aussen},
  }
