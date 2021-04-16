<?php

namespace App\Http\Controllers;

use App\Models\ClusterType;

class ClusterTypeController extends Controller
{
    public function index()
    {
        return ClusterType::all();
    }

    public function show($id)
    {
        return ClusterType::findOrFail($id);
    }
}
