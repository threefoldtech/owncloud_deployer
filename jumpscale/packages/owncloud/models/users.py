from enum import Enum
from jumpscale.core.base import Base, fields
from jumpscale.loader import j


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
    status = fields.Enum(UserStatus)
    time = fields.DateTime()
    deployment_timestamp = fields.DateTime()
    expired_timestamp = fields.DateTime()
    trial_period = fields.Integer(default=20 * 60)
    error_message = fields.String(default="")

    @property
    def is_expired(self):
        return (
            j.data.time.utcnow().timestamp
            > int(self.deployment_timestamp.timestamp()) + self.trial_period
        )
