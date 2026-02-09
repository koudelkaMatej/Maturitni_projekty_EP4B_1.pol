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

$stmt = $conn->prepare("SELECT id, password_hash, best_score FROM users WHERE username=?");
$stmt->bind_param("s", $username);
$stmt->execute();
$res = $stmt->get_result();
$row = $res->fetch_assoc();

if (!$row || !password_verify($password, $row["password_hash"])) {
  http_response_code(401);
  echo json_encode(["ok"=>false, "error"=>"Invalid login"]);
  exit;
}

$token = bin2hex(random_bytes(24));

$stmt2 = $conn->prepare("UPDATE users SET session_token=? WHERE id=?");
$stmt2->bind_param("si", $token, $row["id"]);
$stmt2->execute();

echo json_encode([
  "ok"=>true,
  "token"=>$token,
  "username"=>$username,
  "best_score"=>(int)$row["best_score"]
]);
