from jumpscale.core.base import Base, fields


class UserModel(Base):
    tname = fields.String()
    wallet_address = fields.String()
    email = fields.Email()
    time = fields.DateTime()
    status = fields.String()
