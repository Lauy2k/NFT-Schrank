<?php
$servername = "localhost";
$username = "root";
$password = "raspberry";
$dbname = "sensordaten";

// Verbindung herstellen
$conn = new mysqli($servername, $username, $password, $dbname);

// Verbindung prüfen
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// SQL-Abfrage (korrekte Namen verwenden!)
$sql = "SELECT id, Rf, sensor_id, Temp, time FROM dht22 ORDER BY id DESC LIMIT 3";
$result = $conn->query($sql);

$data = array();

if ($result->num_rows > 0) {
    // Daten auslesen
    while($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
} else {
    $data = array("error" => "Keine Daten gefunden");
}

$conn->close();

// Daten als JSON ausgeben
header('Content-Type: application/json');
echo json_encode($data);
