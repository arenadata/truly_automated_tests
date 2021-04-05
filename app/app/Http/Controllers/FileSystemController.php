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
            'name' => 'required|string|unique:file_systems',
            'description' => 'nullable|string|max:255'
        ]);

        return FileSystem::create($validated);
    }

    public function show($id)
    {
        return FileSystem::findOrFail($id);
    }
}
