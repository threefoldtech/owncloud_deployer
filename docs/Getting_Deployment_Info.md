## Getting Deployment Info

- enter jsng shell

```sh
jsng
```

- execute the commands bellow, USER_NAME is the 3bot name (minus `.3bot` part) of the user you want to get his deployment info.

```sh
tf = j.tools.terraform
i_name=<USER_NAME>
i = tf.get(i_name)
i.show().json
```
