<?php

namespace App\Http\Controllers;

use App\Models\Cluster;
use Illuminate\Http\Request;

class ClusterController extends Controller
{
    public function index()
    {
        return Cluster::all();
    }

    public function store(Request $request)
    {
        $validated = $this->validate($request, [
            'name' => 'required|string|unique:clusters',
            'description' => 'nullable|string|max:255'
        ]);

        return Cluster::create($validated);
    }

    public function show($id)
    {
        return Cluster::findOrFail($id);
    }
}
