<?php
$conn = new mysqli("localhost", "root", "", "jumpking");

$result = $conn->query(
  "SELECT name, height FROM scores ORDER BY height DESC LIMIT 10"
);

$scores = [];
while ($row = $result->fetch_assoc()) {
  $scores[] = $row;
}

echo json_encode($scores);
