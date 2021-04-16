<?php

namespace Database\Seeders;

use App\Models\ClusterType;
use App\Models\FileSystemType;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        for ($i = 0; $i < 2; $i++) {
            ClusterType::create(["name" => str_random(8)]);
            FileSystemType::create(["name" => str_random(8)]);
        }
    }
}
