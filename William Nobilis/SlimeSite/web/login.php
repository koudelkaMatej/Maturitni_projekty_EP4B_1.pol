<?php
require_once "config.php";
$pageTitle = "Login";

$error = "";
if ($_SERVER["REQUEST_METHOD"] === "POST") {
  $u = trim($_POST["username"] ?? "");
  $p = $_POST["password"] ?? "";

  if ($u === "" || $p === "") {
    $error = "Missing username/password.";
  } else {
    $stmt = $conn->prepare("SELECT id, password_hash FROM users WHERE username=?");
    $stmt->bind_param("s", $u);
    $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc();

    if (!$row || !password_verify($p, $row["password_hash"])) {
      $error = "Invalid login.";
    } else {
      $_SESSION["user_id"] = (int)$row["id"];
      $_SESSION["username"] = $u;
      header("Location: index.php");
      exit;
    }
  }
}

include "header.php";
?>
<div class="card">
  <h1>Login</h1>
  <?php if ($error): ?><p style="color:#ff9aa9;"><b><?= htmlspecialchars($error) ?></b></p><?php endif; ?>
  <form method="post">
    <label>Username</label>
    <input name="username" autocomplete="username">
    <label>Password</label>
    <input name="password" type="password" autocomplete="current-password">
    <div style="margin-top:12px;">
      <button type="submit">Login</button>
    </div>
  </form>
</div>
<?php include "footer.php"; ?>
