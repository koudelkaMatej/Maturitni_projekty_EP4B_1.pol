<?php
require_once "db.php";

$res = $conn->query("SELECT username, best_score FROM users ORDER BY best_score DESC, created_at ASC LIMIT 10");

$out = [];
while ($row = $res->fetch_assoc()) {
  $out[] = ["username"=>$row["username"], "best_score"=>(int)$row["best_score"]];
}

echo json_encode(["ok"=>true, "leaderboard"=>$out]);
