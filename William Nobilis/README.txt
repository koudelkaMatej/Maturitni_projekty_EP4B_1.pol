Vloz SlimeSite, index.php, leaderboard.php, submit_score.php do htdocs

Tento dotaz do sql creation v http://localhost/phpmyadmin/index.php
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(32) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  best_score INT NOT NULL DEFAULT 0,
  session_token VARCHAR(64) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Stahni Build z https://drive.google.com/drive/folders/1fY5C0mg3-eucYCJm99K_dZJkp4hSNO_P?usp=drive_link
