<?php
header("Access-Control-Allow-Origin: *"); // ✅ Allow all origins
header("Access-Control-Allow-Methods: POST, GET, OPTIONS"); // ✅ Allow methods
header("Access-Control-Allow-Headers: Content-Type"); // ✅ Allow content type

// Handle preflight (OPTIONS) request
if ($_SERVER["REQUEST_METHOD"] === "OPTIONS") {
    http_response_code(200);
    exit();
}

error_reporting(E_ALL);
ini_set('display_errors', 1);

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $username = escapeshellarg($_POST['username']);
    $password = escapeshellarg($_POST['password']);

    $python_path = "C:\\Users\\GMZ\\Desktop\\vs\\ao3-scheduler\\.venv\\Scripts\\python.exe";
    $cmd = "$python_path login_script.py $username $password 2>&1"; 

    error_log("Executing: " . $cmd);
    $output = shell_exec($cmd);
    error_log("Python Output: " . $output);

    header('Content-Type: application/json');
    echo $output;
} else {
    echo json_encode(["status" => "error", "message" => "Invalid request."]);
}
?>
