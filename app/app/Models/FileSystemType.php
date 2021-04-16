<?php


namespace App\Models;


use Illuminate\Database\Eloquent\Model;

class FileSystemType extends Model
{

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name',
    ];

    public $timestamps = false;

    public function fileSystems()
    {
        return $this->hasMany(FileSystem::class);
    }
}
