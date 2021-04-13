<?php


namespace App\Models;


use Illuminate\Database\Eloquent\Model;

class ClusterType extends Model
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

    public function clusters()
    {
        return $this->hasMany(Cluster::class);
    }
}
