<?php

namespace App\Http\Controllers;

use App\Models\FileSystem;
use Illuminate\Http\Request;

class FileSystemController extends Controller
{
    public function index()
    {
        return FileSystem::all();
    }

    public function store(Request $request)
    {
        $validated = $this->validate($request, [
            'name' => ['required', 'string', 'max:255', 'unique:file_systems'],
            'description' => ['nullable', 'string', 'max:2000'],
            'fs_type_id' => ['required', 'integer', 'exists:file_system_types,id'],
        ]);

        return response()->json(FileSystem::create($validated), 201);
    }

    public function show($id)
    {
        return FileSystem::findOrFail($id);
    }
}
