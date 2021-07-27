<?php

header('Content-Type: text/plain; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST')
	exit("Direct access not supported.");

$redirect = '{{url_for('OM-OSS')}}';
