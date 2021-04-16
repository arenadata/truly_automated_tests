<?php

namespace App\Http\Controllers;

use App\Models\FileSystemType;

class FileSystemTypeController extends Controller
{
    public function index()
    {
        return FileSystemType::all();
    }

    public function show($id)
    {
        return FileSystemType::findOrFail($id);
    }
}
