FROM ubuntu:20.04

LABEL maintainer="hammamw@incubaid.com"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y git curl wget \
                python3-venv \
                python3-pip \
                redis-server \
                tmux \
                nginx \
                build-essential \
    && pip3 install poetry

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - &&\
    apt-get install -y nodejs &&\
    npm install -g npm@latest && \
    npm install --global yarn

RUN wget https://github.com/threefoldtech/zinit/releases/download/v0.1/zinit -O /sbin/zinit \
    && chmod +x /sbin/zinit

RUN apt-get update && apt-get install -y gnupg software-properties-common curl &&\
    curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add - &&\
    apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main" &&\
    apt-get update && apt-get install -y terraform

RUN git clone -b main_fix_docker_image --single-branch https://github.com/threefoldtech/owncloud_deployer.git

WORKDIR /owncloud_deployer
RUN chmod +x ./docker/init.sh

RUN cd jumpscale/packages/owncloud/frontend/ && \
    yarn && yarn build

RUN cd balance_server && \
    yarn

RUN poetry config virtualenvs.create false && poetry install --no-dev
#ENV PATH="$(poetry env info --path)/bin:$PATH"
# terrafrom env variables
ENV TF_SOURCE_MODULE_DIR="/root/tf_source_module"
ENV TF_PLUGIN_CACHE_DIR="/root/.terraform.d/plugin-cache"
ENV TF_IN_AUTOMATION=true

RUN mkdir -p /root/.terraform.d/plugin-cache
COPY tf_source_module /root/tf_source_module
COPY rootfs /

RUN mkdir /data
VOLUME /data

EXPOSE 443 80

CMD ["zinit", "init"]