from enum import Enum
from jumpscale.core.base import Base, fields
from jumpscale.loader import j


def reset_error_message(instance, value):
    if value not in [UserStatus.APPLY_FAILURE, UserStatus.DESTROY_FAILURE]:
        instance.error_message = ""
        instance.save()


class UserStatus(Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    DESTROYING = "DESTROYING"
    DEPLOYED = "DEPLOYED"
    EXPIRED = "EXPIRED"
    APPLY_FAILURE = "APPLY_FAILURE"
    DESTROY_FAILURE = "DESTROY_FAILURE"


class DeploymentModel(Base):
    tname = fields.String()
    email = fields.Email()
    status = fields.Enum(UserStatus, on_update=reset_error_message)
    time = fields.DateTime()
    deployment_timestamp = fields.DateTime()
    expired_timestamp = fields.DateTime()
    trial_period = fields.Integer(default=3 * 30 * 24 * 60 * 60) # 3 months
    error_message = fields.String(default="")

    @property
    def is_expired(self):
        if self.deployment_timestamp.timestamp():
            return (
                j.data.time.utcnow().timestamp
                > int(self.deployment_timestamp.timestamp()) + self.trial_period
            )
        return False
