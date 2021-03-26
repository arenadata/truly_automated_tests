# Truly automated tests example
Sample project for "Truly automated testing" concept demo


## API  Spec

### Methods

 - **/endpoint/**
    - **GET** - List all objects. Will be called **LIST** in further mentions
    - **POST** - Create an object. Will be called **POST** in further mentions
 - **/endpoint/\<obj_id\>/**
    - **GET** - Get exact object data. Will be called **GET** in further mentions

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

Name | Type | Required | Description
---: | --- | --- | ---
id | `integer` | `False` | Auto generated Object Id
name | `string` | `True` | Cluster name
description | `text` | `False` | Cluster description for UI


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

Name | Type | Required | Description
---: | --- | --- | ---
id | `integer` | `False` | Auto generated Object Id
name | `string` | `True` | File system name
description | `text` | `False` | File system description for UI


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

Name | Type | Required | Description
---: | --- | --- | ---
id | `integer` | `False` | Auto generated Object Id
name | `string` | `True` | Connection name
cluster | `integer` | `True` | FK to [Cluster](#cluster)
filesystem | `integer` | `True` | FK to [File system](#file-system)


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

Name | Type | Required | Description
---: | --- | --- | ---
id | `integer` | `False` | Auto generated Object Id
name | `string` | `True` | Backup name
cluster | `integer` | `True` | FK to [Cluster](#cluster)
filesystem | `integer` | `True` | FK to [File system](#file-system)