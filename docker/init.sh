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

# Create a dummy identity to start jsng with Threefold Connect
jsng "ident=j.core.identity.new(\"default\", \"$dummy_tname\", \"$dummy_email\", network=\"$explorer_network\", admins=$ADMINS); ident.register(); ident.save()"

# Create the default threebot
jsng 'j.servers.threebot.new("default"); j.servers.threebot.default.save()'
jsng "j.servers.threebot.default.packages.add(path='/owncloud_deployer/jumpscale/packages/owncloud')"

# Set email server config
jsng "email_server_config = {\"host\": \"$email_host\", \"port\": "$email_port", \"username\": \"$email_username\", \"password\": \"$email_password\"}; j.core.config.set(\"EMAIL_SERVER_CONFIG\", email_server_config)"
