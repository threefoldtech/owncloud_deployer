from enum import Enum
from jumpscale.core.base import Base, fields


class UserStatus(Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    DEPLOYING = "DEPLOYING"
    DESTROYING = "DESTROYING"
    DEPLOYED = "DEPLOYED"
    EXPIRED = "EXPIRED"
    APPLY_FAILURE = "APPLY_FAILURE"
    DESTROY_FAILURE = "DESTROY_FAILURE"

class UserModel(Base):
    tname = fields.String()
    email = fields.Email()
    status = fields.Enum(UserStatus)
    time = fields.DateTime()
    deployment_timestamp = fields.DateTime()
    expired_timestamp = fields.DateTime()
    trial_period = fields.Integer(default=90 * 24 * 60 * 60)
