ARG BASE_IMAGE="alpine:3.11"
ARG NETBOX_VERSION="2.8.1"
ARG S6_VERSION="1.22.1.0"
ARG S6_ARCH="amd64"

########## S6 Overlay Build ##########
FROM "${BASE_IMAGE}" as s6-build
ARG S6_VERSION
ARG S6_ARCH
WORKDIR /tmp
RUN apk add --no-cache \
    curl \
    gnupg \
  && curl \
    --location \
    --output "s6-overlay-${S6_ARCH}.tar.gz" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_VERSION}/s6-overlay-${S6_ARCH}.tar.gz" \
  \
  && curl \
    --location \
    --output "s6-overlay-${S6_ARCH}.tar.gz.sig" \
    "https://github.com/just-containers/s6-overlay/releases/download/v${S6_VERSION}/s6-overlay-${S6_ARCH}.tar.gz.sig" \
  \
  && curl \
    --location \
    --output "key.asc" \
    "https://keybase.io/justcontainers/key.asc" \
  \
  && gpg --import ./key.asc \
  && gpg --verify "s6-overlay-${S6_ARCH}.tar.gz.sig" "s6-overlay-${S6_ARCH}.tar.gz" \
  && mkdir /out \
  && tar xfz "s6-overlay-${S6_ARCH}.tar.gz" -C /out \
  && rm -rf /tmp/*

########## Netbox Build ##########
FROM "${BASE_IMAGE}" as netbox-build
RUN apk add --no-cache \
    build-base \
    cyrus-sasl-dev \
    jpeg-dev \
    libevent-dev \
    libffi-dev \
    libxslt-dev \
    openldap-dev \
    postgresql-dev \
    python3-dev \
  && pip3 install setuptools wheel

# Download and unpack Netbox
WORKDIR /tmp
ARG NETBOX_VERSION
RUN mkdir -p '/out/opt/netbox' \
  && wget "https://github.com/netbox-community/netbox/archive/v${NETBOX_VERSION}.tar.gz" \
  && tar xfz "v${NETBOX_VERSION}.tar.gz" --strip-components 1 -C '/out/opt/netbox' \
  && rm -f "v${NETBOX_VERSION}.tar.gz"

# Build dependencies and put them in wheelhouse for final stage
COPY rootfs/opt/netbox/local_requirements.txt /out/opt/netbox/local_requirements.txt
RUN mkdir -p '/out/usr/local/lib/wheelhouse' \
  && num_cpu=$(grep -c '^processor.*:' /proc/cpuinfo) \
  && num_jobs=$(expr "${num_cpu}" + 1) \
  && export CFLAGS="-g0 -Wl,--strip-all" \
  && export MAKEFLAGS="-j ${num_jobs}" \
  && pip3 wheel \
    --disable-pip-version-check \
    --no-cache-dir \
    --wheel-dir='/out/usr/local/lib/wheelhouse' \
    -r '/out/opt/netbox/requirements.txt' \
    -r '/out/opt/netbox/local_requirements.txt'

########## Netbox ##########
FROM "${BASE_IMAGE}" as netbox

# Copy artifacts from previous build stages
COPY --from=s6-build /out /
COPY --from=netbox-build /out /

# Copy only the local_requirements.txt prior to depdency installation
# for better layer caching
COPY rootfs/opt/netbox/local_requirements.txt /out/opt/netbox/local_requirements.txt

# Install system python dependencies
#
# Note: We will leave the wheelhouse in the image so 
#       upgrade.sh can still run without failing
RUN apk add --no-cache \
    ca-certificates \
    graphviz \
    libevent \
    libffi \
    libjpeg-turbo \
    libldap \
    libressl \
    libsasl \
    libxslt \
    nginx \
    postgresql-libs \
    python3 \
    shadow \
    ttf-ubuntu-font-family \
    tzdata \
    util-linux \
  \
  && python3 -m venv --symlinks /opt/netbox/venv \
  && source /opt/netbox/venv/bin/activate \
  && pip3 install \
    --disable-pip-version-check \
    --find-links=/usr/local/lib/wheelhouse \
    --no-cache-dir \
    --no-index \
    -r '/opt/netbox/requirements.txt' \
    -r '/opt/netbox/local_requirements.txt' \
  && deactivate


COPY rootfs /
ARG NETBOX_VERSION
RUN  echo "Create default directories" \
  && mkdir -p \
    /defaults/data/netbox/media \
    /defaults/data/netbox/reports \
    /defaults/data/netbox/scripts \
  \
  && echo "Move nginx configuration and strip out default site" \
  && mv -n /etc/nginx/* /defaults/data/nginx \
  && rm -f /defaults/data/nginx/conf.d/default.conf \
  && rm -rf /etc/nginx \
  \
  && echo "Configure nginx to log to stdout/stderr" \
  && ln -sf /dev/stdout /var/log/nginx/access.log \
  && ln -sf /dev/stderr /var/log/nginx/error.log \
  \
  && echo Copy defaults to data volume \
  && false | cp --recursive /defaults/* / \
  \
  && echo "Link configurations to data volume" \
  && ln -sf /data/nginx /etc/nginx \
  && ln -sf /data/netbox/configuration.py /opt/netbox/netbox/netbox/configuration.py \
  && ln -sf /data/netbox/gunicorn.py /opt/netbox/gunicorn.py \
  \
  && echo "Create netbox user" \
  && addgroup -g 888 -S netbox \
  && adduser -h /opt/netbox -s /sbin/nologin -G netbox -S -D -u 888 netbox \
  \
  && echo "Create file flag for netbox version" \
  && printf "${NETBOX_VERSION}" > /opt/netbox/netbox_version \
  \
  && echo "Build netbox static assets" \
  && source /opt/netbox/venv/bin/activate \
  && export SECRET_KEY=$(python3 /opt/netbox/netbox/generate_secret_key.py) \
  && python3 /opt/netbox/netbox/manage.py collectstatic --no-input --link \
  \
  && echo "Harden" \
  && rm -rf \
    /etc/acpi \
    /etc/conf.d \
    /etc/crontabs \
    /etc/fstab \
    /etc/init.d \
    /etc/inittab \
    /etc/logrotate.d \
    /etc/mdev.conf \
    /etc/modprobe.d \
    /etc/modules \
    /etc/periodic \
    /etc/rc.conf \
    /etc/runlevels \
    /etc/sysctl* \
    /lib/rc \
    /root \
    /var/spool/cron \
  && sed -i -r '/^(netbox|nginx|root|nobody)/!d' /etc/passwd \
  && sed -i -r '/^(netbox|nginx|root|nobody)/!d' /etc/shadow \
  && sed -i -r '/^(netbox|nginx|root|nobody)/!d' /etc/group \
  && sed -i -r 's#^(.*):[^:]*$#\1:/sbin/nologin#' /etc/passwd \
  && while IFS=: read -r username _; do passwd -l "$username"; done < /etc/passwd || true \
  && find / -xdev -type f -a \( -perm +4000 -o -perm +2000 \) -delete
    


# Add the virtual enviroment to $PATH to implicitly "activate" it
ENV PATH="/opt/netbox/venv/bin:$PATH"

# Make container fail if init scripts fail
ENV S6_BEHAVIOUR_IF_STAGE2_FAILS=2 

ENV NETBOX_VERSION="${NETBOX_VERSION}"
ENV NETBOX_UPGRADE="auto"

WORKDIR /opt/netbox/netbox
ENTRYPOINT ["/init"]
