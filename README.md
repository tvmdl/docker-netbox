# docker-netbox
This is a docker container for [Netbox](https://github.com/netbox-community/netbox).

## Quickstart
Example `docker-compose.yml`:
```yaml
version: '3.7'

services:
  netbox:
    build:
      context: ./netbox
    environment:
      POSTGRES_PASSWORD: example-password
      SUPERUSER_NAME: super
      SUPERUSER_EMAIL: super@localhost
      SUPERUSER_PASSWORD: example-superuser-password
      TZ: UTC
    ports:
      - '8888:8888'
    restart: unless-stopped
    volumes:
      - './volumes/netbox:/data'

  postgres:
    image: postgres:12-alpine
    environment:
      POSTGRES_PASSWORD: example-password
    restart: unless-stopped
    volumes:
      - './volumes/postgres:/var/lib/postgresql/data'
      
  redis:
    image: redis:5-alpine
    command: 'redis-server --appendonly yes'
    restart: unless-stopped
    volumes:
      - './volumes/redis:/data'
      

```

## Configuration
You can configure Netbox by directly modifying configuration files, or optionally using environment variables.

### Configuration files
Configuration files can be modified manually, and are found in the `/data/netbox` volume.

### Environment variables
Some Netbox settings are not simply strings, so the correspodning environment variables may be parsed.  See the `Note` column of the tables below.

#### Required Netbox settings
| Environment Variable | Default | Note |
| --- | --- | --- |
| `POSTGRES_DB` | `postgres` | |
| `POSTGRES_USER` | `postgres` | |
| `POSTGRES_PASSWORD` | `netbox` | |
| `POSTGERS_HOST` | `postgres` | |
| `POSTGRES_PORT` | `5432` | |
| `POSTGRES_CONN_MAX_AGE` | `300` | |
| `REDIS_TASKS_HOST` | `redis` | |
| `REDIS_TASKS_PORT` | `6379` | |
| `REDISK_TASKS_PASSWORD` | none | |
| `REDISK_TASKS_DATABASE` | `0` | |
| `REDISK_TASKS_DEFAULT_TIMEOUT` | `300` | |
| `REDIS_TASKS_SSL` | `False` | |
| `REDIS_CACHE_HOST` | `redis` | |
| `REDIS_CACHE_PORT` | `6379` | |
| `REDIS_CACHE_PASSWORD` | none | |
| `REDIS_CACHE_DATABASE` | `1` | |
| `REDIS_CACHE_SSL` | `False` | |
| `SECRET_KEY` | Automatically generated | If not set, will generate one on startup and save in `/data` volume |

#### Optional Netbox settings
There are many optional settings; the only ones included in this README are those with custom logic used to parse environment variable values into Python data structures.  See the default `configuration.py` for more information.

| Environment Variable | Default | Note |
| --- | --- | --- |
| `ADMINS` | none | Example: `John Doe::john.doe@example.com,Jane Doe::jane.doe@example.com` |
| `CORS_ORIGIN_WHITELIST` | none | `https://hostname.example.com,https://www.hostname.example.com` |
| `CORS_ORIGIN_REGEX_WHITELIST` | none | double-pipe (`\|\|`) delimited regex |
| `EXEMPT_VIEW_PERMISSIONS` | none | comma-delimited list <br> ex: `dcim.site,dcim.region` |
| `STORAGE_CONIG` | none | Value of environment variable will be parsed as JSON |
| `NAPALM_ARGS` | none | Value of environment variable will be parsed as JSON |
| `PLUGINS` | none | Comma-delimited list |
| `PLUGINS_CONFIG` | none | Value of environment variable will be parsed as JSON |
| `REMOTE_AUTH_DEFALT_GROUPS` | none | Comma-delimited list |
| `REMOTE_AUTH_DEFAULT_PERMISSIONS` | none | Comma-delimited list |
| `PLUGINS_CONFIG` | none | Value of environment variable will be parsed as JSON |
| `TIME_ZONE` | `UTC` | If `TIME_ZONE` is unset but `TZ` is, use `TZ` instead of default `UTC` |
