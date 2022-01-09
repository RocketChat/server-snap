# How to update MongoDB

## 1. Enable migration

```sh
chmod +x migrations/pre_refresh/feature_compatibility/00-adopt-version.sh
```

This migration or pre-refresh script will make sure the feature compatibility version of the existing mongodb instance is set correctly for the update to pass through successfully.

```sh
{ is_mongod_running || start_mongod; } &&
  is_mongod_ready &&
    v=$(mongod_version_excluding_patch) &&
      is_mongod_primary &&
        { is_feature_compatibility $v || set_feature_compatibility $v; } &&
          stop_mongod
```

## 2. Add new MongoDB link

TODO: simply this, use a plugin

Go to https://www.mongodb.com/try/download/community and get the archive link of the desired mongodb version. Open snapcraft.yaml and add that to the mongodb part source.

NOTE: use the mongodb-tools part when mongodb >=5.0.0

## 3. Increase epoch

Assuming the current epoch is n, change the epoch to n*. 

From after this, if performing consecutive mongodb updates in a short amount of time (no 100% chance of every install being auto-refreshed to latest revision), increase epoch by 1. See the table below.

| MongoDB    |  epoch |
|------------|--------|
| 1          | n      |
| 2          | n*     |
|  3         | (n+1)* |
|  4         | (n+2)* |
|  5 (final) | (n+3)  |

| MongoDB    | epoch |
|------------|-------|
| 1          | n     |
| 2          | n*    |
|  3 (final) | (n+1) |

## 4. Disable migration

Once snap released wwith desired mongodb version, disable the migration (keeping it won't necessarily do any harm, but why)

```sh
chmod -x migrations/pre_refresh/feature_compatibility/00-adopt-version.sh
```
