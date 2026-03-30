<?php
require_once "config.php";
$pageTitle = "Home";
include "header.php";

$best = null;
if (is_logged_in()) {
  $stmt = $conn->prepare("SELECT best_score FROM users WHERE id=?");
  $stmt->bind_param("i", $_SESSION["user_id"]);
  $stmt->execute();
  $best = $stmt->get_result()->fetch_assoc()["best_score"] ?? 0;
}
?>
<div class="card">
  <h1>Definitely Not Jump King</h1>
  <p class="small">Login to save your best height. Host mode won’t save.</p>

  <?php if (is_logged_in()): ?>
    <p>Your best score: <b><?= (int)$best ?></b></p>
    <p><a class="btn" href="leaderboard.php">View leaderboard</a></p>
  <?php else: ?>
    <p><a class="btn" href="login.php">Login</a> <a class="btn" href="register.php">Register</a></p>
  <?php endif; ?>

  <hr style="border:0;border-top:1px solid #232a46;margin:14px 0;">
  <p class="small">Game download: (put your build zip here later)</p>
</div>
<?php include "footer.php"; ?>
