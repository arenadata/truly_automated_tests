<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class AddClusterType extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('cluster_types', function (Blueprint $table) {
            $table->id();
            $table->string('name');
        });

        Schema::table('clusters', function (Blueprint $table) {
            $table->foreignId('cluster_type_id')->nullable()->constrained('cluster_types');
        });

        // https://stackoverflow.com/questions/3170634/cannot-add-a-not-null-column-with-default-value-null-in-sqlite3
        Schema::table('clusters', function (Blueprint $table) {
            $table->foreignId('cluster_type_id')->nullable(false)->change();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('clusters', function (Blueprint $table) {
            $table->dropColumn('cluster_type_id');
        });

        Schema::drop('cluster_types');
    }
}
