from .users import DeploymentModel
from jumpscale.core.base import StoredFactory

deployment_model = StoredFactory(DeploymentModel)
deployment_model.always_reload = True