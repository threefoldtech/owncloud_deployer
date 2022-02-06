from jumpscale.loader import j
from textwrap import dedent
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from owncloud.models import user_model
from owncloud.models.users import UserStatus

from owncloud.models.lock import Lock

DEPLOYMENT_QUEUE = "DEPLOYMENT_QUEUE"
MAIL_QUEUE = "MAIL_QUEUE"
ROOT_PATH = j.sals.fs.join_paths(j.sals.fs.expanduser("~"), "tf_data")
PLUGIN_DIR = j.sals.fs.join_paths(ROOT_PATH, "tf_plugins")
STATES_DIR = j.sals.fs.join_paths(ROOT_PATH, "tf_states")
SOURCE_MODULE_DIR = j.sals.fs.expanduser("~/tf_source_module")
RETRY = 3

tf_lock = Lock()


class Deployment(BackgroundService):
    def __init__(self, interval=60 * 10, *args, **kwargs):
        """
        Deployment service pulls deployment tasks from redis queue and excutes deployment using terraform client
        """
        super().__init__(interval, *args, **kwargs)
        self.schedule_on_start = True

    def job(self):
        j.logger.debug("Deployment service has started")
        self.deploy()

    def deploy(self):
        """pull tasks from redis queue, apply, retry, and mark deployments as done, or failed"""
        # check if the source module directory is exists and not empty
        if not j.sals.fs.exists(SOURCE_MODULE_DIR) or j.sals.fs.is_empty_dir(
            SOURCE_MODULE_DIR
        ):
            j.logger.critical("source module directory is not exists or empty")
            return

        while True:
            user_info_json = j.core.db.blpop(DEPLOYMENT_QUEUE)[1]
            user_name = j.data.serializers.json.loads(user_info_json)
            try:
                with tf_lock.lock:
                    j.logger.debug(f"deployment service acquired tf lock")
                    user = user_model.get(user_name)
                    user.status = UserStatus.DEPLOYING
                    user.save()
                    j.logger.info(f"Deploying for user {user_name}")
                    client = j.tools.terraform.get(user_name)
                    client.source_module = SOURCE_MODULE_DIR
                    client.plugin_dir = PLUGIN_DIR
                    client.state_dir = j.sals.fs.join_paths(STATES_DIR, user_name)
                    client.save()
                    client.copy_source_module()
                    # export TF_PLUGIN_CACHE_DIR="$HOME/.terraform.d/plugin-cache"
                    # the directory must already exist before Terraform will cache plugins
                    # The plugin cache directory must not also be one of the configured or implied filesystem mirror directories,
                    # since the cache management logic conflicts with the filesystem mirror logic when operating on the same directory.
                    # res = client.providers_mirror()
                    # if not res.is_ok:
                    #     j.logger.warning(
                    #         f"providers mirror command failed. reason: {res.last_error}"
                    #     )

                    res = client.init(upgrade=True, use_plugin_dir=False)
                    if not res.is_ok:
                        j.logger.warning(
                            f"init command failed. reason: {res.last_error}"
                        )
                    res = _apply_user_deployment(client, user_name)
                    if not res.is_ok:
                        j.logger.critical(
                            f"all retries for deployment for user {user_name} has been failed.\nreason for last try failure: {res.last_error}"
                        )
                        user.status = UserStatus.APPLY_FAILURE
                        user.save()
                        continue

                    user.status = UserStatus.DEPLOYED
                    user.deployment_timestamp = j.data.time.utcnow().timestamp
                    user.save()
                    j.logger.info(f"Deployment success for user {user_name}")

                    domain = res.outputs.get("fqdn")

                    if not domain:
                        j.logger.critical(
                            f"failed to get output value 'fqdn' for user {user_name}"
                        )
                        continue

                    admin_name = res.outputs.get("admin_name")
                    if not admin_name:
                        j.logger.critical(
                            f"failed to get output value 'admin_name' for user {user_name}"
                        )
                        continue

                    admin_password = res.outputs.get("admin_password")

                    if not admin_password:
                        j.logger.critical(
                            f"failed to get output value 'admin_password' for user {user_name}"
                        )
                        continue

                _schedule_mail_task(
                    user_name, user.email, domain, admin_name, admin_password
                )
                j.logger.debug(f"deployment service released tf lock")
            except Exception as e:
                j.logger.debug(f"deployment service released tf lock")
                j.logger.error(
                    f"failed to deploy for user {user_name}, error message:\n{e.args}"
                )
                j.logger.exception(f"failed to deploy for user {user_name}", e)
                user.status = UserStatus.APPLY_FAILURE
                user.save()


def _apply_user_deployment(client, name):
    for i in range(RETRY):
        j.logger.debug(f"try {i + 1}/{RETRY} to deploy the instance for user {name}")
        apply_res = client.apply({"user": name})
        if not apply_res.is_ok:
            j.logger.error(
                f"failed to deploy for user {name}, error message:\n{apply_res.last_error}"
            )
            continue
        else:
            # succeed
            return apply_res
    # failed
    state_list_res = client.get_state_list()
    if state_list_res.is_ok and not state_list_res.resources:
        # no need to clean up resources
        return apply_res
    _clean_leftover_resources(client, name)
    return apply_res


def _clean_leftover_resources(client, name):
    for i in range(RETRY):
        j.logger.debug(
            f"try {i + 1}/{RETRY} to clean up the failed deployment for user {name}"
        )
        destroy_res = client.destroy({"user": name})
        if not destroy_res.is_ok:
            j.logger.error(
                f"failed to clean up the the failed deployment for user {name}, error message:\n{destroy_res.last_error}"
            )
            continue
        break


def _schedule_mail_task(user_name, user_email, domain, admin_name, admin_password):
    message = f"""\
        Dear {user_name}
    Your Owncloud instance will be ready in few minutes, please use these credentials to access it. \n
    Domain: {domain}
    Admin username: {admin_name}
    Admin password: {admin_password}
    """
    mail_info = {
        "recipients_emails": user_email,
        "sender": "no-reply@threefold.io",
        "subject": "Owncloud deployment",
        "message": dedent(message),
    }
    j.logger.info(f"pushing mail task for user {user_name}")
    j.core.db.rpush(MAIL_QUEUE, j.data.serializers.json.dumps(mail_info))


service = Deployment()
