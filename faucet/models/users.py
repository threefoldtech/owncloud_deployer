from jumpscale.core.base import Base, fields


class UserModel(Base):
    tname = fields.String()
    wallet_address = fields.String()
    time = fields.DateTime()
