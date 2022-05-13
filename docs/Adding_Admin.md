## Adding an admin

- enter jsng shell

```sh
jsng
```

- execute the commands bellow

```sh
i = j.core.identity.me
i.admins.append("<3bot_name>")
i.save()
exit()
```

- if you running inside docker container, you will need to execute the commands above inside the container.

```sh
docker exec -it owncloud bash
```

- next you will need to restart the container.

```sh
docker restart owncloud
```