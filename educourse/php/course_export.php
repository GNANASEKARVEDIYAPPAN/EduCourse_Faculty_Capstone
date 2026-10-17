<?php
// Optional PHP read-only integration. Run separately under PHP server.
// Reads a JSON file exported by Flask; does not bypass Flask authentication.
$file = __DIR__ . '/sample_export.json';
header('Content-Type: application/json; charset=utf-8');
if (!is_file($file)) { http_response_code(404); echo json_encode(['error'=>'Place a Flask-exported course JSON at php/sample_export.json']); exit; }
$data = json_decode(file_get_contents($file), true);
if (!is_array($data)) { http_response_code(422); echo json_encode(['error'=>'Invalid JSON']); exit; }
echo json_encode(['subject'=>$data['subject']['name'] ?? '', 'record_count'=>count($data['records'] ?? [])], JSON_PRETTY_PRINT);
