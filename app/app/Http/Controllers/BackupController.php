<?php

namespace App\Http\Controllers;

use App\Models\Backup;
use App\Models\Connection;
use Illuminate\Http\Request;

class BackupController extends Controller
{
    public function index()
    {
        return Backup::all();
    }

    public function store(Request $request)
    {
        $validated = $this->validate($request, [
            'name' => 'required|string|unique:backups',
            'cluster_id' => 'required|integer|exists:clusters,id',
            'filesystem_id' => 'required|integer|exists:file_systems,id',
        ]);

        $connection = Connection::where([
            'cluster_id' => $validated['cluster_id'],
            'filesystem_id' => $validated['filesystem_id']
        ])->first();

        if (!empty($connection)) {
            return Backup::create($validated);
        } else {
            return response()->json(['connection' => ['Connection does not exist']], 404);
        }
    }

    public function show($id)
    {
        return Backup::findOrFail($id);
    }
}
