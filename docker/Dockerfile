FROM ubuntu:20.04

LABEL maintainer="hammamw@incubaid.com"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install -y git curl wget \
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
    
RUN git clone https://github.com/threefoldtech/owncloud_deployer.git

WORKDIR owncloud_deployer
RUN chmod +x init.sh
RUN cd balance_server && \
    yarn

RUN poetry config virtualenvs.create false &&  poetry install --no-dev
RUN poetry shell

COPY hcl_content.tf /root/hcl_content.tf
COPY rootfs /

EXPOSE 443 80

CMD ["zinit", "init"]