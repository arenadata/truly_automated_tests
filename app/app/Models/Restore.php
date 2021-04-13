<?php


namespace App\Models;


use Illuminate\Database\Eloquent\Model;

class Restore extends Model
{
    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name', 'timeout', 'backup_id',
    ];

    public $timestamps = false;

    public function backup()
    {
        return $this->belongsTo(Backup::class);
    }
}
