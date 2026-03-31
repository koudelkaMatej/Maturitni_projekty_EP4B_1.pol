<?php if (!isset($pageTitle)) $pageTitle = "SlimeSite"; ?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= htmlspecialchars($pageTitle) ?></title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header class="topbar">
    <div class="wrap">
      <div class="brand"><a href="index.php">SlimeSite</a></div>
      <nav class="nav">
        <a href="leaderboard.php">Leaderboard</a>
        <?php if (isset($_SESSION["user_id"])): ?>
          <span class="pill">Hi, <?= htmlspecialchars($_SESSION["username"]) ?></span>
          <a class="btn" href="logout.php">Logout</a>
        <?php else: ?>
          <a class="btn" href="login.php">Login</a>
          <a class="btn" href="register.php">Register</a>
        <?php endif; ?>
      </nav>
    </div>
  </header>
  <main class="wrap">
