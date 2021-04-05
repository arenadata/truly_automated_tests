<?php


namespace App\Models;


use Illuminate\Database\Eloquent\Model;

class FileSystem extends Model
{
    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name', 'description',
    ];

    protected $attributes = [
        'description' => 'no description provided',
    ];

    public $timestamps = false;

    public function clusters()
    {
        return $this->hasManyThrough(Cluster::class, Connection::class);
    }
}
