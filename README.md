# Truly automated tests example
Sample project for "Truly automated testing" concept demo


## API  Spec

### Methods

 - **/endpoint/**
    - **GET** - List all objects. Will be called **LIST** in further mentions
    - **POST** - Create an object. Will be called **POST** in further mentions
 - **/endpoint/\<obj_id\>/**
    - **GET** - Get exact object data. Will be called **GET** in further mentions

### Types

 - `integer`
    - Positive integer value < 2<sup>31</sup>
 - `string`
    - String up to 255 symbols
 - `text`
    - String with to 2000 symbols

### Cluster

DB cluster object

**Endpoint:** _/cluster/_

#### Allowed methods

Name | Allowed
---: | ---
GET  | `True`
LIST | `True`
POST | `True`

#### Fields

Name | Type | Required | Nullable | Description
---: | --- | --- | --- | ---
id | `integer` | `False` | `False` | Auto generated Object Id
name | `string` | `True` | `False` | Cluster name
description | `text` | `False` | `True` | Cluster description for UI
cluster_type_id | `integer` | `True` | `False` | FK to [Cluster type](#cluster-type)


### Cluster type

Predefined Cluster types
A list of cluster types should be predefined and only available for reading

**Endpoint:** _/cluster-type/_

#### Allowed methods

Name | Allowed
---: | ---
GET  | `True`
LIST | `True`
POST | `False`

#### Fields

Name | Type | Required | Nullable | Description
---: | --- | --- | --- | ---
id | `integer` | `False` | `False` | Auto generated Object Id
name | `string` | `True` | `False` | Cluster type name


### File system

File system for backup storage

Endpoint: _/file-system/_

#### Allowed methods

Name | Allowed
---: | ---
GET  | `True`
LIST | `True`
POST | `True`

#### Fields

Name | Type | Required | Nullable | Description
---: | --- | --- | --- | ---
id | `integer` | `False` | `False` | Auto generated Object Id
name | `string` | `True` | `False` | File system name
description | `text` | `False` | `True` | File system description for UI
fs_type_id | `integer` | `True` | `False` | FK to [File system type](#file-system-type)


### File system type

Predefined File system types
A list of file system types should be predefined and only available for reading

**Endpoint:** _/cluster-type/_

#### Allowed methods

Name | Allowed
---: | ---
GET  | `True`
LIST | `True`
POST | `False`

#### Fields

Name | Type | Required | Nullable | Description
---: | --- | --- | --- | ---
id | `integer` | `False` | `False` | Auto generated Object Id
name | `string` | `True` | `False` | File system type name


### Connection

Connection between a cluster and filesystem

Endpoint: _/connection/_

#### Allowed methods

Name | Allowed
---: | ---
GET  | `True`
LIST | `True`
POST | `True`

#### Fields

Name | Type | Required | Nullable | Description
---: | --- | --- | --- | ---
id | `integer` | `False` | `False` | Auto generated Object Id
name | `string` | `True` | `False` | Connection name
cluster_id | `integer` | `True` | `False` | FK to [Cluster](#cluster)
filesystem_id | `integer` | `True` | `False` | FK to [File system](#file-system)


### Backup

Create backup of cluster to file system.

> [Connection](#connection) for given [Cluster](#cluster) and [File system](#file-system)
> should exist before backup creation 

Endpoint: _/backup/_

#### Allowed methods

Name | Allowed
---: | ---
GET  | `True`
LIST | `True`
POST | `True`

#### Fields

Name | Type | Required | Nullable | Description
---: | --- | --- | --- | ---
id | `integer` | `False` | `False` | Auto generated Object Id
name | `string` | `True` | `False` | Backup name
cluster_id | `integer` | `True` | `False` | FK to [Cluster](#cluster)
filesystem_id | `integer` | `True` | `False` | FK to [File system](#file-system)


### Restore

Restore data from backup.

Endpoint: _/restore/_

#### Allowed methods

Name | Allowed
---: | ---
GET  | `True`
LIST | `True`
POST | `True`

#### Fields

Name | Type | Required | Nullable | Description
---: | --- | --- | --- | ---
id | `integer` | `False` | `False` | Auto generated Object Id
name | `string` | `True` | `False` | Backup name
timeout | `integer` | `True` | `True` | Timeout for restore execution. Unlimited if null
backup_id | `integer` | `True` | `False` | FK to [Backup](#backup)
