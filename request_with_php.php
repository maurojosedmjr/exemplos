<?php

function callAuthFunction($url, $email, $password) {
	$ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    $arrayAuth = array('email' => $email, 'senha' => $password);
    $authDict = json_encode($arrayAuth);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $authDict);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json', 'Cache-Control: no-cache', 'accept: application/json'));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $combined = curl_exec($ch);
    curl_close ($ch);
    return json_decode($combined, TRUE)["access_token"];
}

$urllogin = '';

$email = '';

$senha = '';

$result = callAuthFunction($urllogin, $email, $senha);

// echo $result;

$urlRequest = '';

// Create a new cURL resource
$ch = curl_init($urlRequest);

// Setup request to send json via POST
$data = array(
    'key1' => 'Valor 1',
    'key2' => 'valor 2'
);

$payload = json_encode($data);

echo $payload;
echo "\n\n";

// Attach encoded JSON string to the POST fields
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);

// Set the content type to application/json
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json', "Authorization: Bearer {$result}"));

// Return response instead of outputting
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

// Execute the POST request
$result = curl_exec($ch);

echo $result;
echo "\n\n";

// Close cURL resource
curl_close($ch);

?>
