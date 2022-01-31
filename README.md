# owncloud fremuim deployment

jumpscale based package for owncloud 3 month fremuim deployment

## requirements

- python > 3.8
- js-sdk

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
