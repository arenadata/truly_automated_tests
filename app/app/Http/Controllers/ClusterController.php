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
            'name' => ['required', 'string', 'max:255', 'unique:clusters'],
            'description' => ['nullable', 'string', 'max:2000'],
            'cluster_type_id' => ['required', 'integer', 'exists:cluster_types,id'],
        ]);

        return response()->json(Cluster::create($validated), 201);
    }

    public function show($id)
    {
        return Cluster::findOrFail($id);
    }
}
