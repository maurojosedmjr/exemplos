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

$urlRequest = '';

$ch = curl_init($urlRequest);

$data = array(
    'key1' => 'Valor 1',
    'key2' => 'valor 2'
);

$payload = json_encode($data);

curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);

curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json', "Authorization: Bearer {$result}"));

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$result = curl_exec($ch);

echo $result;
echo "\n\n";

curl_close($ch);

?>
