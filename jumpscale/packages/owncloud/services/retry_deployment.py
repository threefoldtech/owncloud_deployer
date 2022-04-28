from jumpscale.loader import j
from textwrap import dedent
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from jumpscale.packages.owncloud.models import deployment_model
from jumpscale.packages.owncloud.models.users import UserStatus

from jumpscale.packages.owncloud.models.lock import Lock

DEPLOYMENT_QUEUE = "DEPLOYMENT_QUEUE"
MAIL_QUEUE = "MAIL_QUEUE"
RETRY = 5

TF_Lock = Lock()


class RetryDeployment(BackgroundService):
    def __init__(self, interval=60 * 20, *args, **kwargs):
        """
        RetryDeployment service retry failed deployments
        """
        super().__init__(interval, *args, **kwargs)
        self.schedule_on_start = True

    def job(self):
        j.logger.debug("RetryDeployment service has started")
        self.retry_deploy()

    def retry_deploy(self):
        """loop in user model and check if the deployment in APPLY_FAILURE status and retry the deployment"""
        users = deployment_model.list_all()
        for user_name in users:
            user = deployment_model.get(user_name)
            if user.status == UserStatus.APPLY_FAILURE:
                try:
                    user.status = UserStatus.PENDING
                    user.save()
                    j.logger.info(
                        f"pushing the failed instance for user {user.tname} to deploy queue"
                    )
                    j.core.db.rpush(DEPLOYMENT_QUEUE, j.data.serializers.json.dumps(user.tname))
                except Exception as e:
                    user.status = UserStatus.APPLY_FAILURE
                    user.save()
                    j.logger.error(
                        f"failed to retry failed instance for user {user.tname}, error message:\n{e.args}"
                    )

        j.logger.debug("RetryExpired service has finished")


service = RetryDeployment()
