<?php
require_once "config.php";
$pageTitle = "Register";

$error = "";
if ($_SERVER["REQUEST_METHOD"] === "POST") {
  $u = trim($_POST["username"] ?? "");
  $p = $_POST["password"] ?? "";

  if (strlen($u) < 3) $error = "Username must be at least 3 characters.";
  else if (strlen($p) < 4) $error = "Password must be at least 4 characters.";
  else {
    $hash = password_hash($p, PASSWORD_DEFAULT);
    $stmt = $conn->prepare("INSERT INTO users (username, password_hash, best_score, session_token, created_at) VALUES (?, ?, 0, '', NOW())");
    $stmt->bind_param("ss", $u, $hash);

    if ($stmt->execute()) {
      // auto-login
      $_SESSION["user_id"] = (int)$stmt->insert_id;
      $_SESSION["username"] = $u;
      header("Location: index.php");
      exit;
    } else {
      $error = "Username already taken (or DB error).";
    }
  }
}

include "header.php";
?>
<div class="card">
  <h1>Register</h1>
  <?php if ($error): ?><p style="color:#ff9aa9;"><b><?= htmlspecialchars($error) ?></b></p><?php endif; ?>
  <form method="post">
    <label>Username</label>
    <input name="username" autocomplete="username">
    <label>Password</label>
    <input name="password" type="password" autocomplete="new-password">
    <div style="margin-top:12px;">
      <button type="submit">Create account</button>
    </div>
  </form>
</div>
<?php include "footer.php"; ?>
