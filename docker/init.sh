#!/bin/bash

# link model to presistent volume
mkdir -p /data/jsngmodel && ln -s /data/jsngmodel ~/.config/jumpscale

# Edit the default domain with the passed one
sed -i "s/domain = \"waleed.threefold.io\"/domain = \"$domain\"/g" /owncloud_deployer/jumpscale/packages/owncloud/package.toml 

# Create a dummy identity to start jsng with Threefold Connect
jsng "ident=j.core.identity.new(\"default\", \"tftshopident5.3bot\", \"test5@email.com\", network=\"mainnet\", words=\"ginger benefit design struggle match chaos erosion minor hen light awkward candy youth mirror cabbage upper three smoke boy animal science net poverty pond\", admins=$ADMINS); ident.register(); ident.save()"

# Create the default threebot
jsng 'j.servers.threebot.new("default"); j.servers.threebot.default.save()'
jsng "j.servers.threebot.default.packages.add(path='/owncloud_deployer/jumpscale/packages/owncloud')"

# Set email server config
jsng "email_server_config = {\"host\": \"$email_host\", \"port\": "$email_port", \"username\": \"$email_username\", \"password\": \"$email_password\"}; j.core.config.set(\"EMAIL_SERVER_CONFIG\", email_server_config)"
