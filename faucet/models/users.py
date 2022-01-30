from jumpscale.core.base import Base, fields


class UserModel(Base):
    tname = fields.String()
    email = fields.Email()
    status = fields.String()
    time = fields.DateTime()
