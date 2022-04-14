# Owncloud Fremuim Deployment

jumpscale based package for owncloud 3 month fremuim deployment

- user will ask to acquire his free instance
- devops will approve the request
- deployment will be done from the pre-configured account
- user will receive email with deployment status and credentials
- destruction service will destroy the deployment after the trial is over (90 days)
- an email will be sent to user with trial is over
- there's also a service to check wallet balance if it's < 1000 it'll send email to support

## requirements

- python >= 3.8
- js-sdk
- node > 14 && yarn
- Terraform

### Frontend

- Build `make build`
- Push your changes

### Docker

```bash
docker run -ti --name owncloud -e domain="<domain_name>" -e email_host="<mail_server_hostname>" -e email_port=<port> -e email_username="<email>" -e email_password="<password>" -e MNEMONICS="<MNEMONICS>" -e CHAIN_URL="wss://tfchain.dev.grid.tf/ws" -e NETWORK="dev" -e ADMINS="['<3bot_name>']" -e ALERT_EMAIL="<support_mail_address>" -p 80:80 -p 443:443 threefolddev/owncloud_deployer:0.1
```

#### ENV VARS 
##### js-sdk env:
  
- `domain`: domain of the site which will host the package (done in package.toml)
- `email_host`, `email_port`, `email_username`, `email_password`: configurations of mail server
- `ADMINS`: list of system admins (3bot names) that will manage requests
- `ALERT_EMAIL`: email which will receive wallet alerts
- `NO_CERT`: if set to any non-empty value, server will start without a certificate.
##### Balance server env:
- `CHAIN_URL`: url for the tfchain according to network
- `MNEMONICS`: words of the account being used to deploy from

##### terraform and terraform client env:
- `MNEMONICS`: words of the account being used to deploy from
- `NETWORK`: grid network to deploy on, one of: [dev, test, main]. default to dev.
- `TF_SOURCE_MODULE_DIR`: the configuration directory, will be copied into the target directory before any other initialization steps are run.
- `TF_PLUGIN_CACHE_DIR`: enable caching. optional.
- `TF_IN_AUTOMATION`: if set to any non-empty value, Terraform adjusts its output to avoid suggesting specific commands to run next. This can make the output more consistent and less confusing. optional.

### Helm

Refer to helm docs in [helmcharts/owncloud/README.md](helmcharts/owncloud/README.md)

#### local running

1- Export previous variables
2- Configure mail client

  ```bash
  j.core.config.set("EMAIL_SERVER_CONFIG", {'host': 'smtp.gmail.com', 'port': '587', 'username': '', 'password': ''}) 
  ```

3- build frontend
3- Add the package to the server
4- Start the server
5- Go to <https://domain> you'll find the website

### User Endpoints

- `/`: in this page user will enter his email address, if it's empty TF-Connect email will be taken

- `/#/requests`: in this page dev-ops can approve requests to start deployment and check the statuses

#### Endpoints

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

##### `/owncloud/api/requests` [POST]

- Register new user with email if provided (optional)

Example body : `{email: "someone@example.com}`

Responses:

- If user is not registered before, you'll have `201` + successful msg
- If user is registered before, you'll get `409` + error msg

##### `/owncloud/api/deployment` [POST] (admin only)

- for Support to deploy instances for users and mark them as done

- Example body : `[waleedhammam]`

Responses:

- If success, you'll have `200` + successful msg
- If error, you'll have error code + error msg

##### `/owncloud/api/balance` [GET] (admin only)

- Get current balance

Example response

```json
{
    "balance": "9733.4300505"
}
```

##### `/owncloud/api/requests/export` [GET] (admin only)

- Download a copy of all registered users as csv
