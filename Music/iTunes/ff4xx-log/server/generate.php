<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Database connection settings
$servername = "localhost";
$username = "your_db_user";
$password = "your_db_password";
$dbname = "license_keys";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(['success' => false, 'message' => 'Connection failed']));
}

// Get parameters
$count = isset($_GET['count']) ? intval($_GET['count']) : 1;
$duration_days = isset($_GET['days']) ? intval($_GET['days']) : 30;

$keys = [];

for ($i = 0; $i < $count; $i++) {
    // Generate random key in format: XXXX-XXXX-XXXX-XXXX
    $key = sprintf(
        "%04X-%04X-%04X-%04X",
        mt_rand(0, 0xFFFF),
        mt_rand(0, 0xFFFF),
        mt_rand(0, 0xFFFF),
        mt_rand(0, 0xFFFF)
    );
    
    $expiry = date('Y-m-d H:i:s', strtotime("+$duration_days days"));
    
    $stmt = $conn->prepare("INSERT INTO licenses (license_key, expiry_date, created_at) VALUES (?, ?, NOW())");
    $stmt->bind_param("ss", $key, $expiry);
    
    if ($stmt->execute()) {
        $keys[] = [
            'key' => $key,
            'expiry_date' => $expiry
        ];
    }
    $stmt->close();
}

echo json_encode([
    'success' => true,
    'message' => count($keys) . ' keys generated',
    'keys' => $keys
]);

$conn->close();
?>
