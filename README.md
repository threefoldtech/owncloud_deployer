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

### Frontend

- Build `make build`
- Push your changes

### Docker

```bash
docker run -ti --name owncloud   waleedhammam/owncloud-dep -e domain="waleed.threefold.io" -e email_host="smtp.gmail.com" -e email_port=587 -e email_username="<email>" -e email_password="<password>" -e MNEMONICS="<MNEMONICS>" -e CHAIN_URL="wss://tfchain.dev.grid.tf/ws" -e NETWORK="dev" -e ADMINS=["waleedhammam.3bot"] -e ALERT_EMAIL="waleed.hammam@gmail.com"
```

#### env
  
- `domain`: domain of the site which will host the package (done in package.toml)
- `email_host`, `email_port`, `email_username`, `email_password`: configurations of mail server
- `MNEMONICS`: words of the account being used to deploy from
- `CHAIN_URL`: url for the tfchain according to network
- `NETWORK`: network to deploy on (default: dev)
- `ADMINS`: list of system admins that will manage requests
- `ALERT_EMAIL`: email which will receive wallet alerts

##### terraform and terraform client env

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
