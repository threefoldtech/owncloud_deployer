from jumpscale.loader import j
from textwrap import dedent
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from owncloud.models import user_model
from owncloud.models.users import UserStatus
from jumpscale.tools.terraform.terraform import TFStatus

from owncloud.models.lock import Lock
DEPLOYMENT_QUEUE = "DEPLOYMENT_QUEUE"
MAIL_QUEUE = "MAIL_QUEUE"
TF_HCL_CONTENT_PATH = j.sals.fs.expanduser("~/hcl_content.tf")

tf_lock = Lock()
class Deployment(BackgroundService):
    def __init__(self, interval=60 * 10, *args, **kwargs):
        """
        Deployment service is using data from redis queue and deploy it
        """
        super().__init__(interval, *args, **kwargs)
        self.schedule_on_start = True

    def job(self):
        j.logger.debug("Deployment service has started")
        self.deploy()

    def deploy(self):
        """Pick deployments from redis queue, retry deployment, mark deployments
        """
        while True:
            user_info_json = j.core.db.blpop(DEPLOYMENT_QUEUE)[1]
            try:
                if not user_info_json:
                    j.logger.error("queue is empty!")
                    break
                tf_lock.lock.acquire()
                j.logger.debug(f"deployment service acquired tf lock")
                username = j.data.serializers.json.loads(user_info_json)
                user = user_model.get(username)
                user.status = UserStatus.DEPLOYING
                user.save()
                j.logger.info(f"Deploying for user {username}")
                client = j.tools.terraform.get(username)
                client.hcl_content = j.sals.fs.read_file(TF_HCL_CONTENT_PATH)
                client.providers_mirror()
                client.init(use_plugin_dir=True)
                if not self._apply_terraform(client, username):
                    j.logger.critical(f"all retries for deployment for user {username} has been failed")
                    user.status = UserStatus.APPLY_FAILURE
                    user.save()
                    continue

                user.status = UserStatus.DEPLOYED
                user.deployment_timestamp = j.data.time.utcnow().timestamp
                user.save()
                j.logger.info(f"Deployment success for user {username}")
                
                return_code, domain = client.get_output(output_name="fqdn")

                if return_code != 0:
                    j.logger.critical(f"failed to get output value 'fqdn' for user {username}, {domain}")
                    continue
                admin_username = "admin"
                
                return_code, admin_password = client.get_output(output_name="admin_passwords")
                
                if return_code != 0:
                    j.logger.critical(f"failed to get output value 'admin_passwords' for user {username}, {admin_password}")
                    continue

                # send email
                message = f"""\
                    Dear {user.tname}
                Your Owncloud instance will be ready in few minutes, please use these credentials to access it. \n
                Domain: {domain}
                Admin username: {admin_username}
                Admin password: {admin_password}
                """
                mail_info = {
                    "recipients_emails": user.email,
                    "sender": "no-reply@threefold.io",
                    "subject": "Owncloud deployment",
                    "message": dedent(message),
                }
                j.logger.info(f"Sending mail for user {username}")
                j.core.db.rpush(MAIL_QUEUE, j.data.serializers.json.dumps(mail_info))
            except Exception as e:
                j.logger.error(f"failed to deploy for user {username}, error message:\n{e.args}")
                j.logger.exception(f"failed to deploy for user {username}", e)
                user.status = UserStatus.APPLY_FAILURE
                user.save()
            finally:
                tf_lock.lock.release()
                j.logger.debug(f"deployment service released tf lock")

                

    def _destroy_terraform(self, client, name):
        for i in range(3):
            j.logger.debug(f"try {i + 1}/3 to clean up the failed deployment for user {name}")
            return_code, res = client.destroy({"user":name})
            if return_code != 0:
                j.logger.error(f"failed to clean up the the failed deployment for user {name}, error message:\n{res[-1]}")
                continue
            break


    def _apply_terraform(self, client, name):
        for i in range(3):
            j.logger.debug(f"try {i + 1}/3 to deploy the instance for user {name}")
            if client.status == TFStatus.APPLIED:
                return True
            return_code, res = client.apply({"user":name})
            if return_code != 0:
                j.logger.error(f"failed to deploy for user {name}, error message:\n{res[-1]}")
                continue
            return True
        rc, resources = client.get_state_list()
        if rc == 0 and resources:
            self._destroy_terraform(client, name)
        return False

service = Deployment()
