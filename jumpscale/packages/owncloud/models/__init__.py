from .users import UserModel
from jumpscale.core.base import StoredFactory

user_model = StoredFactory(UserModel)
user_model.always_reload = True