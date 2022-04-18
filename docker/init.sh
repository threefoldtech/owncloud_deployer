#!/bin/bash

# prepare random tname and email
rand_id=$(cat /dev/urandom | tr -dc 'a-z' | fold -w 10 | head -n 1)
dummy_tname=$rand_id".3bot"
dummy_email=$rand_id"@email.com"

# set the explorer network based on tfchain network
if [[ $NETWORK == "main" ]]; then
    explorer_network='mainnet'
else
    explorer_network='testnet'
fi

# link model to presistent volume
mkdir -p /data/jsngmodel && ln -s /data/jsngmodel ~/.config/jumpscale

# Edit the default domain with the passed one
sed -i "s/domain = \"waleed.threefold.io\"/domain = \"$domain\"/g" /owncloud_deployer/jumpscale/packages/owncloud/package.toml 

# Edit the default support ssh key with the passed one
[[ ! -z "${SUPPORT_PUBLIC_SSH_KEY}" ]] && sed -i "s:\"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSkhNAIP22RH/sQx7alFS6vcqw1OAQUkC5MLv6t3L78YVTRv+/owSqIqCQHr2+zfb3aJijsxj9nqg54rVkEiCXOkT6IE/MGWSP6O/x/cCG8J7AT+OCCjo9IB/+V3CA8yREHi7ggqPv6hEfNoa1AMbnxqxT7a+5sJUVd14/Ib9OQKWBCXzosa0SjTY/RO1SrL93E80N+SJQRBCMemzlepn4wLDWvqs7DiruY+g9E2CskhDijt4iJCuNFZzAcTS3UeqxOG2QfLK2zc8M9/AycMcEyHn94Lml6V75Lk09iLB9QGTGsa4oAD3GFLce4VoKKZx0e6lwwnMNoAHKhBEMFmO5 root@waleed-ng\":\"$SUPPORT_PUBLIC_SSH_KEY\":g" /root/tf_source_module/main.tf

# Create a dummy identity to start jsng with Threefold Connect
jsng "ident=j.core.identity.new(\"default\", \"$dummy_tname\", \"$dummy_email\", network=\"$explorer_network\", admins=$ADMINS); ident.register(); ident.save()"

# Create the default threebot
jsng 'j.servers.threebot.new("default"); j.servers.threebot.default.save()'
jsng "j.servers.threebot.default.packages.add(path='/owncloud_deployer/jumpscale/packages/owncloud')"

# Set email server config
jsng "email_server_config = {\"host\": \"$email_host\", \"port\": "$email_port", \"username\": \"$email_username\", \"password\": \"$email_password\"}; j.core.config.set(\"EMAIL_SERVER_CONFIG\", email_server_config)"
