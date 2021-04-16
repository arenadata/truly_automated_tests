<?php

namespace App\Http\Controllers;

use App\Models\Backup;
use App\Models\Connection;
use App\Models\Restore;
use Illuminate\Http\Request;

class RestoreController extends Controller
{
    public function index()
    {
        return Restore::all();
    }

    public function store(Request $request)
    {
        $validated = $this->validate($request, [
            'name' => ['required', 'string', 'max:255', 'unique:backups'],
            'timeout' => ['required', 'integer', 'min:0', 'max:2147483647', 'nullable'],
            'backup_id' => ['required', 'integer', 'exists:backups,id'],
        ]);

        return response()->json(Restore::create($validated), 201);
    }

    public function show($id)
    {
        return Restore::findOrFail($id);
    }
}
