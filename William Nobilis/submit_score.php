<?php
$conn = new mysqli("localhost", "root", "", "jumpking");

$data = json_decode(file_get_contents("php://input"), true);

$name = $data["name"];
$height = $data["height"];

$stmt = $conn->prepare("INSERT INTO scores (name, height) VALUES (?, ?)");
$stmt->bind_param("si", $name, $height);
$stmt->execute();

echo "OK";
