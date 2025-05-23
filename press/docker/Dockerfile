# syntax = docker/dockerfile:experimental
FROM ubuntu:20.04

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND noninteractive

ENV OPENBLAS_NUM_THREADS 1
ENV MKL_NUM_THREADS 1

ENV TZ=Asia/Ho_Chi_Minh
# Install essential packages
RUN --mount=type=cache,target=/var/cache/apt apt-get update \
  && apt-get install --yes --no-install-suggests --no-install-recommends \
  # Essentials
  build-essential \
  git \
  mariadb-client \
  libmariadb-dev \
  pv \
  ntp \
  wget \
  curl \
  supervisor \
  # Dependencies for SSH access
  openssh-server \
  nano \
  vim \
  less \
  htop \
  iputils-ping \
  telnet \
  # Dependencies for adding Python PPA
  software-properties-common \
  gnupg \
  # weasyprint dependencies
  libpango-1.0-0 \
  libharfbuzz0b \
  libpangoft2-1.0-0 \
  libpangocairo-1.0-0 \
  # wkhtmltopdf dependencies
  ca-certificates \
  fontconfig \
  libfreetype6 \
  libjpeg-turbo8 \
  libpng16-16 \
  libx11-6 \
  libxcb1 \
  libxext6 \
  libxrender1 \
  xfonts-75dpi \
  xfonts-base \
  # pycups dependencies
  gcc \
  file \
  libcups2-dev \
  # s3-attachment dependencies
  libmagic1 \
  && rm -rf /var/lib/apt/lists/* \
  `#stage-pre-essentials`

COPY --chown=root:root supervisord.conf /etc/supervisor/supervisord.conf

#set-timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# Install Redis from PPA
RUN --mount=type=cache,target=/var/cache/apt curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg \
  && echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb focal main" | tee /etc/apt/sources.list.d/redis.list \
  && apt-get update \
  && apt-get install --yes --no-install-suggests --no-install-recommends \
  redis-server \
  && rm -rf /var/lib/apt/lists/* `#stage-pre-redis`

# Install Python from DeadSnakes PPA
ENV {{ doc.get_dependency_version("PYTHON_VERSION") }}
RUN --mount=type=cache,target=/var/cache/apt add-apt-repository ppa:deadsnakes/ppa \
  && apt-get update \
  && apt-get install --yes --no-install-suggests --no-install-recommends \
  python${PYTHON_VERSION} \
  python${PYTHON_VERSION}-dev \
  python${PYTHON_VERSION}-venv \
  python3-distutils \
#    {% if not remove_distutils -%}
#    python${PYTHON_VERSION}-distutils \
#    {%- endif %}
#    python${PYTHON_VERSION}-venv \
  && rm -rf /var/lib/apt/lists/* \
  `#stage-pre-python`


# Install wkhtmltopdf
ENV {{ doc.get_dependency_version("WKHTMLTOPDF_VERSION") }}
{% if doc.get_dependency_version("WKHTMLTOPDF_VERSION").split(" ")[1] == '0.12.6' %}
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb \
  && dpkg -i wkhtmltox_0.12.6-1.focal_amd64.deb \
  && rm wkhtmltox_0.12.6-1.focal_amd64.deb \
  `#stage-pre-wkhtmltopdf`
{% elif doc.get_dependency_version("WKHTMLTOPDF_VERSION").split(" ")[1] == '0.12.5' %}
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.focal_amd64.deb \
  && dpkg -i wkhtmltox_0.12.5-1.focal_amd64.deb \
  && rm wkhtmltox_0.12.5-1.focal_amd64.deb \
  `#stage-pre-wkhtmltopdf`
{% elif doc.get_dependency_version("WKHTMLTOPDF_VERSION").split(" ")[1] == '0.12.4' %}
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz \
  && tar -xvf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz \
  && mv wkhtmltox/bin/wkhtmlto* /usr/local/bin/ \
  && rm -rf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz wkhtmltox \
  `#stage-pre-wkhtmltopdf`
{% endif %}

RUN curl -fsSL https://code-server.dev/install.sh | sh `#stage-pre-code-server`

# Install Fonts
RUN git clone --progress --depth 1 https://github.com/frappe/fonts.git /tmp/fonts \
  && rm -rf /etc/fonts && mv /tmp/fonts/etc_fonts /etc/fonts \
  && rm -rf /usr/share/fonts && mv /tmp/fonts/usr_share_fonts /usr/share/fonts \
  && rm -rf /tmp/fonts \
  && fc-cache -fv \
  `#stage-pre-fonts`


# Set max_allowed_packet to 512 MB for mysqldump
RUN echo "[mysqldump]\nmax_allowed_packet              = 512M" > /etc/mysql/conf.d/mysqldump.cnf

{% if doc.apt_packages %}
# Install Additional APT Packages
RUN --mount=type=cache,target=/var/cache/apt apt-get update \
  && apt-get install --yes --no-install-suggests --no-install-recommends \
  {{ doc.apt_packages }} \
  && rm -rf /var/lib/apt/lists/* \
  `#stage-pre-apt-packages`
{% endif %}

RUN ln -s /usr/bin/mysqldump /usr/bin/mariadb-dump

RUN useradd -ms /bin/bash frappe
USER frappe
WORKDIR /home/frappe


# Install Node using NVM
ENV NVM_DIR /home/frappe/.nvm
ENV {{ doc.get_dependency_version("NVM_VERSION") }}
ENV {{ doc.get_dependency_version("NODE_VERSION") }}

RUN wget https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh \
  && bash install.sh \
  && . "/home/frappe/.nvm/nvm.sh" \
  && nvm install ${NODE_VERSION} \
  && nvm use v${NODE_VERSION} \
  && nvm alias default v${NODE_VERSION} \
  && rm install.sh \
  && nvm cache clear \
  `#stage-pre-node`

ENV PATH "$PATH:/home/frappe/.nvm/versions/node/v${NODE_VERSION}/bin"

# Install Yarn
RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 npm install -g yarn `#stage-pre-yarn`

RUN npm config set registry http://registry.npmjs.org/

# Install Bench
ENV PATH "$PATH:/home/frappe/.local/bin"

RUN wget https://bootstrap.pypa.io/get-pip.py && python${PYTHON_VERSION} get-pip.py `#stage-pre-pip`
ENV {{ doc.get_dependency_version("BENCH_VERSION") }}
RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 python${PYTHON_VERSION} -m pip install --upgrade frappe-bench==${BENCH_VERSION} `#stage-bench-bench`

RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 python${PYTHON_VERSION} -m pip install Jinja2~=3.0.3
RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 python${PYTHON_VERSION} -m pip install --upgrade setuptools

#RUN git config --global init.defaultBranch main
RUN git config --global advice.detachedHead false
RUN git config --global --add safe.directory /home/frappe/context/apps/frappe/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/helpdesk/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/lms/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/wiki/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/print_designer/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_rtg/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/raven/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/payments/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/drive/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_dms/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_sfc_hr/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_service_v2/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_account_service/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_audit/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/go1_cms/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/gameplan/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/builder/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/crm/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_sfc_integrations/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/webshop/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/erpnext/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/hrms/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_localization/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/woocommerceconnector/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/fastwork_integrations/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/insights/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/email_delivery_service/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/fastwork_accounting/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/lending/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_ess_registration/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/posawesome/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/getpos/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/clefincode_chat/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/nl_attendance_timesheet/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/doctype_permission/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/tldraw_whiteboard/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/meeting_management/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/frappe_better_list_view/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/desk_navbar_extended/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/ecommerce_integrations/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/dht_co/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/project_control/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/waterai/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_sfa/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/roadai/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_ats/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/i_van/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_gridviewfull/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/frappe_whatsapp/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_pms/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/cargo_management/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbw_integration_dms/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/woocommerce_fusion/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbwd_nissin/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/mbwd_gobross/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/erpnext_telegram_integration/.git
RUN git config --global --add safe.directory /home/frappe/context/apps/vas/.git

ENV PYTHONUNBUFFERED 1

# For the sake of completing the step
RUN `#stage-bench-env`

{% for v in doc.environment_variables %}
ENV {{v.key}} {{ v.value }}
{% endfor %}

# Install Frappe app
RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 --mount=type=bind,source=apps/frappe,target=/home/frappe/context/apps/frappe bench init --python /usr/bin/python${PYTHON_VERSION} --no-backups --frappe-path file:///home/frappe/context/apps/frappe frappe-bench `#stage-apps-frappe`
WORKDIR /home/frappe/frappe-bench

RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 /home/frappe/frappe-bench/env/bin/pip install pycups==2.0.1

# Install Redisearch 2.0 from precompiled binaries
COPY --chown=frappe:frappe redis /home/frappe/frappe-bench/redis

COPY --chown=frappe:frappe common_site_config.json /home/frappe/frappe-bench/sites/common_site_config.json

RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 /home/frappe/frappe-bench/env/bin/pip install wheel

# Install other apps
{% for app in doc.apps %}
{% if app.app != "frappe" %}

RUN --mount=type=cache,target=/home/frappe/.cache,uid=1000,gid=1000 --mount=type=bind,source=apps/{{ app.app }},target=/home/frappe/context/apps/{{ app.app }} bench get-app file:///home/frappe/context/apps/{{ app.app }} `#stage-apps-{{ app.app }}`

{% endif %}
{% endfor %}


COPY --chown=frappe:frappe config /home/frappe/frappe-bench/config
COPY --chown=frappe:frappe apps.txt /home/frappe/frappe-bench/sites/apps.txt


ENV FRAPPE_HARD_LINK_ASSETS True

EXPOSE 8000 9000 2200 8088
CMD ["supervisord"]
