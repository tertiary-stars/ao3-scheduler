<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $username = escapeshellarg($_POST['username']);
    $password = escapeshellarg($_POST['password']);

    // Use full Python path
    $python_path = "C:\\Users\\GMZ\\Desktop\\vs\\ao3-scheduler\\.venv\\Scripts\\python.exe";
    $cmd = "$python_path backend/login_script.py $username $password";

    error_log("Executing: " . $cmd);
    $output = shell_exec($cmd);
    error_log("Python Output: " . $output);

    header('Content-Type: application/json');
    echo $output; // ✅ Ensure output is printed
} else {
    echo json_encode(["status" => "error", "message" => "Invalid request."]);
}
?>
