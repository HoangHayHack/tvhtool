<?php
header("Content-Type: application/json; charset=UTF-8");

$db = "users_total.txt";

if (!file_exists($db)) {
    file_put_contents($db, "");
}

$API_KEY = "Api_Key_TranVanHoang-TVH";

function getIP() {
    if (!empty($_SERVER['HTTP_CLIENT_IP'])) return $_SERVER['HTTP_CLIENT_IP'];
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) return explode(",", $_SERVER['HTTP_X_FORWARDED_FOR'])[0];
    return $_SERVER['REMOTE_ADDR'];
}

$ip = getIP();
$api_key = isset($_GET['api_key']) ? $_GET['api_key'] : "";

if ($api_key !== $API_KEY) {
    echo json_encode([
        "status" => "API Key Không Hợp Lệ",
        "error" => "Từ Chối Truy Cập"
    ], JSON_PRETTY_PRINT);
    exit;
}

$lines = file($db, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

if (!in_array($ip, $lines)) {
    file_put_contents($db, $ip . PHP_EOL, FILE_APPEND);
}

echo json_encode([
    "ip" => $ip,
    "total_users" => count(file($db, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES))
], JSON_PRETTY_PRINT);