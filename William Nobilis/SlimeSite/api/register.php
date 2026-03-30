<?php
require_once "db.php";

$body = json_decode(file_get_contents("php://input"), true);
$username = trim($body["username"] ?? "");
$password = $body["password"] ?? "";

if ($username === "" || $password === "") {
  http_response_code(400);
  echo json_encode(["ok"=>false, "error"=>"Missing username/password"]);
  exit;
}

if (!preg_match('/^[a-zA-Z0-9_]{3,32}$/', $username)) {
  http_response_code(400);
  echo json_encode(["ok"=>false, "error"=>"Username must be 3-32 chars, letters/numbers/_"]);
  exit;
}

$hash = password_hash($password, PASSWORD_DEFAULT);

$stmt = $conn->prepare("INSERT INTO users (username, password_hash) VALUES (?, ?)");
$stmt->bind_param("ss", $username, $hash);

if (!$stmt->execute()) {
  http_response_code(409);
  echo json_encode(["ok"=>false, "error"=>"Username already exists"]);
  exit;
}

echo json_encode(["ok"=>true]);
