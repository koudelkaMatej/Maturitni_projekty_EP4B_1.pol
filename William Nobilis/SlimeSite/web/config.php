<?php
session_start();

// IMPORTANT: website uses db_connect (no JSON headers)
require_once __DIR__ . "/../api/db_connect.php";

function is_logged_in(): bool {
    return isset($_SESSION["user_id"]);
}

function require_login() {
    if (!is_logged_in()) {
        header("Location: login.php");
        exit;
    }
}
