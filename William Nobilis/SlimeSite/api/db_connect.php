<?php
// api/db_connect.php (DB only, no headers)

$host = "localhost";
$db   = "slimegame";
$user = "root";
$pass = ""; // XAMPP default

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    http_response_code(500);
    die("DB connection failed");
}

$conn->set_charset("utf8mb4");
