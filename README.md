# docker-netbox
This is a docker container for [Netbox](https://github.com/netbox-community/netbox) based on Alpine that uses the [S6-Overlay](https://github.com/just-containers/s6-overlay).


## Quickstart
Example `docker-compose.yml` (netbox superuser creds will be logged on startup):
```yaml
version: '3.7'

services:
  netbox:
    build:
      context: https://github.com/tvmdl/docker-netbox.git#master
    environment:
      POSTGRES_PASSWORD: example-password
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
### Container Startup
| Environment Variable | Default | Note |
| --- | --- | --- |
| `TZ` | `UTC` | Sets the timezone for the container |
| `PGID` | `888` | The process group ID.  The container will change ownership of the `/data` volume on startup to match this. |
| `PUID` | `888` | The process user ID.  The container will change ownership of the `/data` volume on startup to match this. |
| `NO_START_SERVICES` | n/a | When set with any value, will prevent all services from starting.  Useful if you want to `docker run ... /bin/ash` without netbox actually starting |
| `NO_START_NETBOX` | n/a | When set with any value, will prevent NGINX/Netbox from starting. Can be used to split Netbox and Netbox Redis Queue services into separate containers. |
| `NO_START_REDIS_QUEUE` | n/a | When set with any value, will prevent Netbox's redis queue worker from starting. Can be used to split Netbox and Netbox Redis Queue services into separate containers. |
| `NETBOX_UPGRADE` | `auto` | When `auto`, will run Netbox's `upgrade.sh` each on startup if the netbox version (tracked in the `/data` volume) increments.  When `always`, will always run the `upgrade.sh` script.  If `never`, will not run the `upgrade.sh` ever |
| `NO_CREATE_SUPERUSER` | n/a | If set, will skip netbox superuser creation. |
| `SUPERUSER_NAME` | `superuser` | The name of the superuser to be created/updated on container startup |
| `SUPERUSER_EMAIL` | `superuser@localhost` | The email address of the superuser to be created/updated on container startup |
| `SUPERUSER_PASSWORD` | Dynamically generated | If container generates the password, will log the password on startup |
| `SUPERUSER_TOKEN` | Dynamically generated | If container generates the token, will log the token on startup |

### NGINX
NGINX can be configured from the `/data/nginx` directory.

### Netbox
To configure netbox, you can either use the configuration files in the `/data/netbox/` directory, or use environment variables.  Additionally, you can create an `ldap_config.py` file in the `/data/netbox/` directory for LDAP support.

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
| `SECRET_KEY` | Dynamically generated | If not set, will generate one on startup and save in `/data` volume |

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
| `TIME_ZONE` | `UTC` | If `TIME_ZONE` is unset, use value of `TZ` environment variable.  If neither are set, use default |
