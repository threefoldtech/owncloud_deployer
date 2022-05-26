# Owncloud Deployer (OCD)

a provisioning portal for [Owncloud](https://owncloud.com/)  and automation cloud tool based on js-sdk and Terraform, enables the DevOps team to automate the OC VM provisioning on the Threefold revolutionary grid, handle users
requests and manage deployments lifecycle in an efficient way.

Users can experience the Owncloud product on the ThreeFold grid as a freemium for a 3-months trial.

## Provisioning process / User experience.

- User will ask to acquire his free instance after authenticated with the threefold connect mobile app. optionally provide an alternative email address.
- DevOps will approve the request from the admin dashboard.
- provisioning will be automatically done/retried for approved requests. the pre-configured account/wallet will be billed.
- User will receive an email with deployment status and credentials.
- Destroy service will check predictably and destroy the deployment after the preconfigure trial period is over (90 days).
- An email will be sent to the user after the trial is over.
- There's also a service to check wallet balance if it's < 1000 it'll send an email to support email.

## requirements

- python >= 3.8
- js-sdk
- node > 14 && yarn
- Terraform

### Frontend

- Build `make build`
- Push your changes

### Docker
#### Running using Docker-compose
the recommended method to run the deployer in production is using docker-compose.

make sure to add your variables to `owncloud-deployer-variables.env` file. check `owncloud-deployer-variables.env.example` for a example configurations.

then just do

```sh
docker-compose up -d
```

when you spin the service, by default it will use `latest` tag to pull the deployer image of the latest released version. for the latest build image enhancements and fixes from our current sprint, you can use `edge` Tag or even specify a specific image version. before `up` command execute the code below

```sh
export OD_IMAGE_TAG=edge
```

#### Update Owncloud-Deployer
you can update the running container easily

```sh
docker-compose pull
docker-compose up -d --remove-orphans
docker image prune -f # optionally
```

#### Restart Owncloud-Deployer
```sh
docker-compose restart owncloud-deployer
```
Note: If you make changes to your docker-compose.yml configuration or changes to environment variables these changes are not reflected after running this command.

#### running using docker

you can spin the container by executing the command below, not recommended in production.

```bash
docker run -ti --name owncloud -e domain='<domain_name>' -e letsencryptemail='<email_address>' -e email_host='<mail_server_hostname>' -e email_port=<port> -e email_username='<email>' -e email_password='<password>' -e MNEMONICS='<MNEMONICS>' -e CHAIN_URL='wss://tfchain.dev.grid.tf/ws' -e NETWORK='dev' -e ADMINS="['<3bot_name>']" -e ALERT_EMAIL='<support_mail_address>' -e SUPPORT_PUBLIC_SSH_KEY='<public ssh key>' -e RESTIC_REPOSITORY='<RESTIC_REPOSITORY_URL>' -e RESTIC_PASSWORD='<RESTIC_REPOSITORY_PASSWORD>' -e AWS_ACCESS_KEY_ID='<MY_ACCESS_KEY_ID>' -e AWS_SECRET_ACCESS_KEY='<MY_SECRET_ACCESS_KEY>' -p 80:80 -p 443:443 threefolddev/owncloud_deployer:latest
```

 Note: Docker will create a local volume without a name. The result will be a long unique id string for the volume that contains no reference to the container it's attached to. Unless Docker is told to remove volumes when containers are removed, these 'anonymous' volumes will remain, unlikely to be used again.

#### ENV VARS 
##### js-sdk env:
  
- `domain`: domain of the site which will host the package.
- `letsencryptemail`: let's Encrypt admin email to receive expiry notices when your certificate is coming up for renewal.
- `email_host`, `email_port`, `email_username`, `email_password`: configurations of mail server.
- `ADMINS`: list of system admins (3bot names) that will manage requests.
- `ALERT_EMAIL`: email which will receive wallet alerts.
- `NO_CERT`: if set to any non-empty value, the server will start without a certificate.
- `ACME_URL`: URL of the custom ACME server, otherwise letsencrypt will be used.
##### Balance server env:
- `CHAIN_URL`: URL for the tfchain according to network.
- `MNEMONICS`: words of the account being used to deploy from.

##### terraform and terraform client env:
- `MNEMONICS`: words of the account being used to deploy from.
- `NETWORK`: grid network to deploy on, one of [dev, test, main]. default to dev.
- `TF_SOURCE_MODULE_DIR`: the configuration directory, will be copied into the target directory before any other initialization steps are run.
- `TF_PLUGIN_CACHE_DIR`: enable caching. optional.
- `TF_IN_AUTOMATION`: if set to any non-empty value, Terraform adjusts its output to avoid suggesting specific commands to run next. This can make the output more consistent and less confusing. optional.
- `SUPPORT_PUBLIC_SSH_KEY`: public ssh key to be added to Owncloud instances's  ~/.ssh/authorized_keys.

##### Restic Backup configuration - optional:
- `RESTIC_REPOSITORY`: The repository location where your backups will be saved. can be stored locally, or on some remote server or service. read here for more information on [restic](https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html).
- `RESTIC_PASSWORD`: Backup password. If you lose it, you won’t be able to access data stored in the repository.
  
  For an Amazon S3 or S3-compatible server, you will need also to provide the following environment variables with the credentials you obtained while creating the bucket.
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Helm

Refer to helm docs in [helmcharts/owncloud/README.md](helmcharts/owncloud/README.md)

### Install from Source Code

1 - install System requirements

```sh
apt-get update
apt-get install -y git python3-venv python3-pip redis-server tmux nginx build-essential restic
# install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
# install nodejs
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
# install yarn
curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/yarnkey.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
apt-get update && sudo apt-get install -y yarn
# install terraform
apt-get update && apt-get install -y gnupg software-properties-common curl
curl -fsSL https://apt.releases.hashicorp.com/gpg | apt-key add -
apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
apt-get update && apt-get install -y terraform
```

2 - clone the repo
```sh
git clone https://github.com/threefoldtech/owncloud_deployer.git
```

3 - Prepare the environment and install the python dependencies
```sh
cd owncloud_deployer
poetry install # source $HOME/.poetry/env
```

4 - make sure your terraform configuration file in place
```sh
cp docker/tf_source_module/main.tf $HOME/tf_source_module
```

5 - create the cache dir
```
mkdir -p $HOME/.terraform.d/plugin-cache
```

6 - install the node balance server dependencies:
```sh
yarn --cwd ./balance_server
```

7 - build frontend if needed

8 - activate the environment
```sh
poetry shell
```

9 - Export required env variables
```sh
export MNEMONICS="<YOUR-MNEMONICS>"
export CHAIN_URL="wss://tfchain.dev.grid.tf/ws"
export TF_SOURCE_MODULE_DIR="$HOME/tf_source_module"
export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
export NETWORK=dev # or test 
export TF_IN_AUTOMATION=true
```

10 - start the Node balance server
```sh
node balance_server/index.js &  # 
```

11 - start JSNG shell
```sh
jsng
```

12 - Configure the server
```
ident=j.core.identity.new("default", "ownclouddeployertest10.3bot", "ownclouddeployertest10@incubaid.com", network="testnet", admins=["samehabouelsaad.3bot"]); ident.register(); ident.save()
j.servers.threebot.new("default"); j.servers.threebot.default.save()
j.core.config.set("EMAIL_SERVER_CONFIG", {'host': 'smtp.gmail.com', 'port': '587', 'username': '', 'password': ''}) 
j.servers.threebot.default.packages.add(path='/root/owncloud_deployer/jumpscale/packages/owncloud', domain=<domain>, letsencryptemail=<letsencryptemail>)
```

13 - start the server
```
threebot start --local
```

14 - The server is running at http://localhost:8080 and https://localhost:8443

### User Endpoints

- `/owncloud/`: in this page user will enter his email address, if it's empty TF-Connect email will be taken

- `/owncloud/#/requests`: in this page dev-ops can approve requests to start deployment and check the statuses

#### API Endpoints

##### `/owncloud/api/requests` [GET] (admin only)

- Get all registered users with statuses as a list.

Example response

```json
    [
        {
        "tname": "waleedhammam",
        "email": "waleed.hammam@gmail.com",
        "status": "DONE",
        "time": 1643638522
        }
    ]

```

##### `/owncloud/api/requests` [POST] (admin only)

- Register new user with email if provided (optional)

Example body: `{email: "someone@example.com}`

Responses:

- If the user is not registered before, you'll have `201` + successful msg
- If the user is registered before, you'll get `409` + error msg

##### `/owncloud/api/deployment` [POST] (admin only)

- for Support to deploy instances for users and mark them as done

- Example body: `[waleedhammam]`

Responses:

- If succeded, you'll have `200` + successful msg
- If error, you'll have an error code + error msg

##### `/owncloud/api/balance` [GET] (admin only)

- Get the current balance

Example response

```json
{
    "balance": "9733.4300505"
}
```

##### `/owncloud/api/requests/export` [GET] (admin only)

- Download a copy of all registered users as CSV

### Advanced Usage
refer to [docs/](docs/)
