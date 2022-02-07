# Owncloud Fremuim Deployment

jumpscale based package for owncloud 3 month fremuim deployment

## requirements

- python > 3.8
- js-sdk
- npm > 14 && yarn

## Endpoints

### `/owncloud/api/requests` [GET] (admin only)

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

### `/owncloud/api/requests` [POST]

- Register new user with email if provided (optional)

Example body : `{email: "someone@example.com}`

Responses:

- If user is not registered before, you'll have `201` + successful msg
- If user is registered before, you'll get `409` + error msg

### `/owncloud/api/deployment` [POST] (admin only)

- for Support to deploy instances for users and mark them as done

- Example body : `[waleedhammam]`

Responses:

- If success, you'll have `200` + successful msg
- If error, you'll have error code + error msg

### `/owncloud/api/balance` [GET] (admin only)

- Get current balance

Example response

```json
{
    "balance": "9733.4300505"
}
```

### `/owncloud/api/requests/export` [GET] (admin only)

- Download a copy of all registered users as csv

### Frontend

- Build go to `jumpscale/packages/owncloud/frontend` and do `yarn && yarn build`
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
  
