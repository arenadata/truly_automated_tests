<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class AddFileSystemType extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('file_system_types', function (Blueprint $table) {
            $table->id();
            $table->string('name');
        });

        Schema::table('file_systems', function (Blueprint $table) {
            $table->foreignId('fs_type_id')->nullable()->constrained('file_system_types');
        });

        // https://stackoverflow.com/questions/3170634/cannot-add-a-not-null-column-with-default-value-null-in-sqlite3
        Schema::table('file_systems', function (Blueprint $table) {
            $table->foreignId('fs_type_id')->nullable(false)->change();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::table('file_systems', function (Blueprint $table) {
            $table->dropColumn('fs_type_id');
        });

        Schema::drop('file_system_types');
    }
}
