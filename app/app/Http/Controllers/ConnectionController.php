<?php

namespace App\Http\Controllers;

use App\Models\Cluster;
use App\Models\Connection;
use Illuminate\Http\Request;

class ConnectionController extends Controller
{
    public function index()
    {
        return Connection::all();
    }

    public function store(Request $request)
    {
        $validated = $this->validate($request, [
            'name' => ['required', 'string', 'max:255', 'unique:connections'],
            'cluster_id' => ['required', 'integer', 'exists:clusters,id'],
            'filesystem_id' => ['required', 'integer', 'exists:file_systems,id'],
        ]);

        return response()->json(Connection::create($validated), 201);
    }

    public function show($id)
    {
        return Connection::findOrFail($id);
    }
}
