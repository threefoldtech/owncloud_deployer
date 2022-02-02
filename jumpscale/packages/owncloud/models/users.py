from enum import Enum
from jumpscale.core.base import Base, fields


class UserStatus(Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILURE = "FAILURE"


class UserModel(Base):
    tname = fields.String()
    email = fields.Email()
    status = fields.Enum(UserStatus)
    time = fields.DateTime()
    deployment_timestamp = fields.DateTime()
