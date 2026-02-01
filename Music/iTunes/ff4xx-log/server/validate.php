<?php
// validate.php - PostgreSQL version
// $pdo connection is already established in index.php

// Get POST data
$json = file_get_contents('php://input');
$data = json_decode($json, true);

$key = isset($data['key']) ? $data['key'] : '';
$hwid = isset($data['hwid']) ? $data['hwid'] : '';

if (empty($key) || empty($hwid)) {
    echo json_encode([
        'valid' => false,
        'message' => 'Invalid request: Missing key or HWID'
    ]);
    exit();
}

// Check if key creation is enabled
$stmt = $pdo->query("SELECT value FROM server_settings WHERE key = 'key_validation_enabled' LIMIT 1");
$validation_enabled = $stmt ? $stmt->fetchColumn() : '1';

if ($validation_enabled === '0') {
    echo json_encode([
        'valid' => false,
        'message' => 'Key validation temporarily disabled'
    ]);
    exit();
}

// Check if key exists and is valid
$stmt = $pdo->prepare("SELECT * FROM licenses WHERE license_key = ? AND (hwid = ? OR hwid IS NULL OR hwid = '') AND expiry_date > NOW() AND status = 'active'");
$stmt->execute([$key, $hwid]);
$row = $stmt->fetch(PDO::FETCH_ASSOC);

if ($row) {
    // If HWID is not set, bind it to this device
    if (empty($row['hwid'])) {
        $updateStmt = $pdo->prepare("UPDATE licenses SET hwid = ?, last_used = NOW() WHERE license_key = ?");
        $updateStmt->execute([$hwid, $key]);
    } else {
        // Update last used time
        $updateStmt = $pdo->prepare("UPDATE licenses SET last_used = NOW() WHERE license_key = ?");
        $updateStmt->execute([$key]);
    }
    
    echo json_encode([
        'valid' => true,
        'message' => 'Key activated successfully!',
        'expiry_date' => $row['expiry_date']
    ]);
} else {
    echo json_encode([
        'valid' => false,
        'message' => 'Invalid key or already bound to another device'
    ]);
}
?>
