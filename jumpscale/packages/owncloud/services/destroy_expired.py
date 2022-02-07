from jumpscale.loader import j
from textwrap import dedent
from jumpscale.tools.servicemanager.servicemanager import BackgroundService
from owncloud.models import deployment_model
from owncloud.models.users import UserStatus

from owncloud.models.lock import Lock

MAIL_QUEUE = "MAIL_QUEUE"
RETRY = 3

TF_Lock = Lock()


class DestroyExpired(BackgroundService):
    def __init__(self, interval=60 * 5, *args, **kwargs):
        """
        DestroyExpired service cleans up expired deployments
        """
        super().__init__(interval, *args, **kwargs)
        self.schedule_on_start = True

    def job(self):
        j.logger.debug("DestroyExpired service has started")
        self.destroy()

    def destroy(self):
        """loop in user model and check if the deployment is expired"""
        users = deployment_model.list_all()
        for user_name in users:
            user = deployment_model.get(user_name)
            if user.status in [UserStatus.DEPLOYED, UserStatus.DESTROY_FAILURE]:
                # check if the deployment is expired
                if user.is_expired:
                    try:
                        with TF_Lock.lock:
                            j.logger.debug(f"destroy_expired service acquired tf lock")
                            # to avoid notifying the user / seting the expired timestamp multiple times
                            if user.status == UserStatus.DEPLOYED:
                                j.logger.info(
                                    f"user {user.tname} deployment is expired"
                                )
                                user.expired_timestamp = j.data.time.utcnow().timestamp
                                user.save()
                                _schedule_mail_task(user.tname, user.email)
                            user.status = UserStatus.DESTROYING
                            user.save()
                            j.logger.info(
                                f"Destroying the expired instance for user {user.tname}"
                            )
                            client = j.tools.terraform.get(user.tname)
                            res = _destroy_user_deployment(client, user.tname)
                            if not res.is_ok:
                                j.logger.critical(
                                    f"all retries for destroying deployment for user {user.tname} has been failed"
                                )
                                user.error_message = res.last_error
                                user.status = UserStatus.DESTROY_FAILURE
                                user.save()
                                continue

                            j.logger.info(
                                f"Expired Deployment destroyed successfully for user {user.tname}"
                            )
                            user.status = UserStatus.EXPIRED
                            user.save()
                        j.logger.debug(f"destroy_expired service released tf lock")
                    except Exception as e:
                        user.status = UserStatus.DESTROY_FAILURE
                        user.save()
                        j.logger.debug(f"destroy_expired service released tf lock")
                        j.logger.error(
                            f"failed to destroy expired instance for user {user.tname}, error message:\n{e.args}"
                        )
                        j.logger.exception(f"failed to deploy for user {user.tname}", e)
                else:
                    j.logger.info(f"user {user.tname} is still in trial period, skip")
        j.logger.debug("DestroyExpired service has finished")


def _destroy_user_deployment(client, name):
    for i in range(3):
        j.logger.debug(
            f"try {i + 1}/{RETRY} to destroy the expired deployment for user {name}"
        )
        res = client.destroy(vars={"user": name})
        if not res.is_ok:
            j.logger.error(
                f"failed to destroy the the failed deployment for user {name}, error message:\n{res.last_error}"
            )
            continue
        break
    return res


def _schedule_mail_task(user_name, user_email):
    message = f"""\
    Dear {user_name}, \n
        Your deployment is expired.
    """
    mail_info = {
        "recipients_emails": user_email,
        "sender": "no-reply@threefold.io",
        "subject": "Your free Owncloud deployment is expired",
        "message": dedent(message),
    }

    j.logger.info(f"pushing mail task for user {user_name}")
    j.core.db.rpush(MAIL_QUEUE, j.data.serializers.json.dumps(mail_info))


service = DestroyExpired()
