<?php
// generate_api.php - API version of key generator (for internal use)

if (!isset($conn)) {
    die(json_encode(['success' => false, 'error' => 'Database not connected']));
}

$count = isset($_GET['count']) ? intval($_GET['count']) : 1;
$duration_days = isset($_GET['days']) ? intval($_GET['days']) : 30;

$keys = [];

for ($i = 0; $i < $count; $i++) {
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
?>
