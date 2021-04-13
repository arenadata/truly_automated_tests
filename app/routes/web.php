<?php

/** @var \Laravel\Lumen\Routing\Router $router */

/*
|--------------------------------------------------------------------------
| Application Routes
|--------------------------------------------------------------------------
|
| Here is where you can register all of the routes for an application.
| It is a breeze. Simply tell Lumen the URIs it should respond to
| and give it the Closure to call when that URI is requested.
|
*/

$router->get('/', function () use ($router) {
    return $router->app->version();
});

$router->group(['prefix' => 'cluster'], function () use ($router) {
    $router->get('/', 'ClusterController@index');
    $router->post('/', 'ClusterController@store');
    $router->get('/{id}', 'ClusterController@show');
});

$router->group(['prefix' => 'cluster-type'], function () use ($router) {
    $router->get('/', 'ClusterTypeController@index');
    $router->get('/{id}', 'ClusterTypeController@show');
});

$router->group(['prefix' => 'file-system'], function () use ($router) {
    $router->get('/', 'FileSystemController@index');
    $router->post('/', 'FileSystemController@store');
    $router->get('/{id}', 'FileSystemController@show');
});

$router->group(['prefix' => 'fs-type'], function () use ($router) {
    $router->get('/', 'FileSystemTypeController@index');
    $router->get('/{id}', 'FileSystemTypeController@show');
});

$router->group(['prefix' => 'connection'], function () use ($router) {
    $router->get('/', 'ConnectionController@index');
    $router->post('/', 'ConnectionController@store');
    $router->get('/{id}', 'ConnectionController@show');
});

$router->group(['prefix' => 'backup'], function () use ($router) {
    $router->get('/', 'BackupController@index');
    $router->post('/', 'BackupController@store');
    $router->get('/{id}', 'BackupController@show');
});

$router->group(['prefix' => 'restore'], function () use ($router) {
    $router->get('/', 'RestoreController@index');
    $router->post('/', 'RestoreController@store');
    $router->get('/{id}', 'RestoreController@show');
});
