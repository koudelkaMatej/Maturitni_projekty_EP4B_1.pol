<?php
require_once "config.php";
$pageTitle = "Leaderboard";
include "header.php";

$res = $conn->query("SELECT username, best_score, created_at
                     FROM users
                     ORDER BY best_score DESC, created_at ASC
                     LIMIT 50");
?>
<div class="card">
  <h1>Leaderboard</h1>
  <table>
    <thead>
      <tr><th>#</th><th>Player</th><th>Best Score</th><th>Joined</th></tr>
    </thead>
    <tbody>
      <?php $i=1; while ($row = $res->fetch_assoc()): ?>
        <tr>
          <td><?= $i++ ?></td>
          <td><?= htmlspecialchars($row["username"]) ?></td>
          <td><b><?= (int)$row["best_score"] ?></b></td>
          <td class="small"><?= htmlspecialchars($row["created_at"]) ?></td>
        </tr>
      <?php endwhile; ?>
    </tbody>
  </table>
</div>
<?php include "footer.php"; ?>
