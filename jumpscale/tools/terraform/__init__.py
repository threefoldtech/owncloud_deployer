def export_module_as():
    from jumpscale.core.base import StoredFactory
    from .terraform import Terraform

    return StoredFactory(Terraform)