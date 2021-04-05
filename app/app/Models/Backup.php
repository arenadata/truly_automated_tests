<?php


namespace App\Models;


use Illuminate\Database\Eloquent\Model;

class Backup extends Model
{
    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name', 'cluster_id', 'filesystem_id',
    ];

    public $timestamps = false;

    public function cluster()
    {
        return $this->belongsTo(Cluster::class);
    }

    public function filesystem()
    {
        return $this->belongsTo(FileSystem::class);
    }
}
