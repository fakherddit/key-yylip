<?php
// Main entry point for Render deployment
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// PostgreSQL connection
$db_url = "postgresql://dylip_key_user:TwbqpTuAggFaAXhIX7Q7pMmJIih5vEQe@dpg-d5v88bl6ubrc73c8tlqg-a.oregon-postgres.render.com/dylip_key";
$db = parse_url($db_url);

$pdo = new PDO(
    "pgsql:host={$db['host']};dbname=" . ltrim($db['path'], '/'),
    $db['user'],
    $db['pass']
);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

// Check if server is enabled
$stmt = $pdo->query("SELECT value FROM server_settings WHERE key = 'server_enabled' LIMIT 1");
$server_enabled = $stmt ? $stmt->fetchColumn() : '1';

if ($server_enabled === '0' && $_SERVER['REQUEST_URI'] !== '/health' && !strpos($_SERVER['REQUEST_URI'], 'telegram-webhook')) {
    http_response_code(503);
    echo json_encode(['error' => 'Server temporarily disabled by admin']);
    exit();
}

// Route handling
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

switch ($path) {
    case '/':
    case '/health':
        echo json_encode(['status' => 'ok', 'service' => 'ST FAMILY License Server']);
        break;
        
    case '/validate':
        require 'validate.php';
        break;
        
    case '/generate':
        require 'generate_api.php';
        break;
        
    case '/telegram-webhook':
        require 'telegram_bot.php';
        break;
        
    default:
        http_response_code(404);
        echo json_encode(['error' => 'Endpoint not found']);
}
?>
