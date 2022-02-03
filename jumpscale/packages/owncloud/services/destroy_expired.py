from jumpscale.loader import j
from textwrap import dedent
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from owncloud.models import user_model
from owncloud.models.users import UserStatus

MAIL_QUEUE = "MAIL_QUEUE"
#TF_HCL_CONTENT_PATH = j.sals.fs.expanduser("~/hcl_content.tf")
TRIAL_PERIOD = 60 * 5 # for testing purposes only

class DestroyExpired(BackgroundService):
    def __init__(self, interval=60 * 10, *args, **kwargs):
        """
        DestroyExpired service cleans up expired deployments
        """
        super().__init__(interval, *args, **kwargs)
        self.schedule_on_start = True

    def job(self):
        j.logger.debug("DestroyExpired service has started")
        self.destroy()

    def destroy(self):
        """loop in user model and check if the deployment is expired
        """
        users = user_model.list_all()
        for user_name in users:
            user = user_model.get(user_name)
            if user.status in [UserStatus.DEPLOYED, UserStatus.DESTROY_FAILURE]:
                # get the trail period for this user
                trail_period = TRIAL_PERIOD
                notify_user = False
                # check if the deployment is expired
                if j.data.time.utcnow().timestamp > int(user.deployment_timestamp.timestamp()) + trail_period:
                    # to avoid notifying the user / seting the expired timestamp multiple times
                    if user.status == UserStatus.DEPLOYED:
                        notify_user = True
                        user.expired_timestamp = j.data.time.utcnow().timestamp
                    j.logger.info(f"user {user.tname} deployment is expired")
                    message = f"""\
                    Dear {user.tname}, \n
                        Your deployment is expired.
                    """
                    mail_info = {
                        "recipients_emails": user.email,
                        "sender": "no-reply@threefold.io",
                        "subject": "Your free Owncloud deployment is expired",
                        "message": dedent(message),
                    }
                    try:
                        if notify_user:
                            j.core.db.rpush(MAIL_QUEUE, j.data.serializers.json.dumps(mail_info))
                        user.status = UserStatus.DESTROYING
                        user.save()
                        j.logger.info(f"Destroying the expired instance for user {user.tname}")
                        client = j.tools.terraform.get(user.tname)
                        # client.hcl_content = j.sals.fs.read_file(TF_HCL_CONTENT_PATH)
                        # client.providers_mirror()
                        # client.init(use_plugin_dir=True)
                        if not self._destroy_terraform(client, user.tname):
                            j.logger.critical(f"all retries for destroying deployment for user {user.tname} has been failed")
                            user.status = UserStatus.DESTROY_FAILURE
                            user.save()
                            continue

                        
                        j.logger.info(f"Expired Deployment destroyed successfully for user {user.tname}")
                        user.status = UserStatus.EXPIRED
                        user.save()

                    except Exception as e:
                        j.logger.error(f"failed to destroy expired instance for user {user.tname}, error message:\n{e.args}")
                        j.logger.exception(f"failed to deploy for user {user.tname}", e)
                        user.status = UserStatus.DESTROY_FAILURE
                        user.save()
                else:
                    j.logger.info(f"user {user.tname} is still in trial period, skip")
            # j.logger.info(f"user {user.tname} is not in trial period, skip")
        j.logger.debug("DestroyExpired service has finished")


    def _destroy_terraform(self, client, name):
        for i in range(3):
            j.logger.debug(f"try {i} to destroy the expired deployment for user {name}")
            return_code, res = client.destroy({"user":name})
            if return_code != 0:
                j.logger.error(f"failed to destroy the the failed deployment for user {name}, error message:\n{res[-1]}")
                continue
            return True
        return False

service = DestroyExpired()
