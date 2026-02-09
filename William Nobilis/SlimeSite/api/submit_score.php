<?php
require_once "db.php";

$body = json_decode(file_get_contents("php://input"), true);
$token = $body["token"] ?? "";
$score = (int)($body["score"] ?? 0);

if ($token === "") {
  http_response_code(400);
  echo json_encode(["ok"=>false, "error"=>"Missing token"]);
  exit;
}

$stmt = $conn->prepare("SELECT id, best_score FROM users WHERE session_token=?");
$stmt->bind_param("s", $token);
$stmt->execute();
$res = $stmt->get_result();
$row = $res->fetch_assoc();

if (!$row) {
  http_response_code(401);
  echo json_encode(["ok"=>false, "error"=>"Invalid token"]);
  exit;
}

$current = (int)$row["best_score"];

if ($score > $current) {
  $stmt2 = $conn->prepare("UPDATE users SET best_score=? WHERE id=?");
  $stmt2->bind_param("ii", $score, $row["id"]);
  $stmt2->execute();
  echo json_encode(["ok"=>true, "updated"=>true, "best_score"=>$score]);
} else {
  echo json_encode(["ok"=>true, "updated"=>false, "best_score"=>$current]);
}
