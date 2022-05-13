## Destroying Deployed Instance
- enter jsng shell

```sh
jsng
```

- execute the commands bellow, USER_NAME is the 3bot name (minus `.3bot` part) of the user you want to destroy his instance.

```sh
tf = j.tools.terraform
i_name=<USER_NAME>
i = tf.get(i_name)
i.destroy(vars={'user':i_name})
i._clean_state_dir() # for deleting all the files in the state dir
```

### Destroying All Deployed Instances 

caution: this will destroy all deployed instances.
caution: Don't execute this in production unless you know what you are doing.

```sh
tf = j.tools.terraform

for i_name in tf.list_all():
    i = tf.get(i_name)
    i.destroy(vars={'user':i_name})
    i._clean_state_dir()

exit()
```

## Deleting deployment request

users won't be able to request new instance unless the requests db is cleaned.

caution: make sure to not delete a request for a deployed instance unless the instance was destroyed. otherwise the deployer won't have a record of this instance and it will stay alive even after the expected expiration date and till its contract deleted from the blockchain.

```sh
from jumpscale.packages.owncloud.models import deployment_model
d_name=<USER_NAME>
d = deployment_model.delete(d_name) # delete the deployment request
```

if what you want is reverting the request to `NEW` status instead of deleted it, you can this by executing the following commands:

```sh
from jumpscale.packages.owncloud.models import deployment_model
d_name=<USER_NAME>
d = deployment_model.get(d_name)
d.status = 'NEW'
d.save()
```