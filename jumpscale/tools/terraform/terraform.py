"""
# Terrafrom client

Tool to create terraform managed infrastructures.

## prerequisites
Make sure to install terraform(https://www.terraform.io/downloads)
On linux it can be installed as follows:

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform
```

its recommended to set environment variable TF_IN_AUTOMATION to any non-empty value.
its recommended to set TF_PLUGIN_CACHE_DIR= to exists dir to be used as a cache dir for plugin download.
also you could set any provider specific input variables in environment variables.

## Usage

### Basic usage

```python
# get new instance of terraform
>>> tf = j.tools.terraform.get("samehabouelsaad")
# optionally specify extra environment variables to be set for terraform command.
>>> instance.extra_env = {'MNEMONICS': 'mnemonics',
                      'NETWROK': 'test'}
# specifiy the dir conatins the terraform configuration (files),
# so it can be copied into the instance working directory to be used.
>>> tf.source_module = "/path/to/terraform/configuration/dir"
# you can override the default path for both state_dir and plugin_dir, but not necessary if you like the default.
>>> tf.state_dir = "/path/to/state/dir"
>>> tf.plugin_dir = "/path/to/plugin/dir"
>>> tf.save()

>>> tf.status
<TFStatus.CREATED: 1>

# the given module {source_module} will be copied into the instance state directory.
# it will raise an error if the dir is not found.
>>> tf.copy_source_module()
# terraform providers mirror, populate the PLUGIN_DIR with the required terraform plugins
>>> res = tf.providers_mirror()
>>> res.is_ok
True

# terraform init, we will use the previously downloaded plugins from last step 
>>> res = tf.init(use_plugin_dir=True)
>>> res.is_ok
True

# terrafrom validate, check if the .tf file is valid
>>> res = tf.validate_hcl()
>>> res.is_ok
True
>>> res.json
{'format_version': '1.0', 'valid': True, 'error_count': 0, 'warning_count': 0, 'diagnostics': []}

>>> res = tf.plan(vars={"user": tf.instance_name})
>>> res.is_ok
True
>>> res.changes_present
True
>>> res.plan_summary
{'add': 6, 'change': 0, 'remove': 0, 'operation': 'plan'}

# terrafrom apply
>>> res = tf.apply(vars={'user': 'samehabouelsaad'})
>>> res.is_ok
False
res.errors
["Error: didn't find a suitable node"]

>>> tf.status
<TFStatus.FAILED_TO_APPLY: 4>

>>> res = tf.apply(vars={'user': 'samehabouelsaad'})
>>> res.is_ok
True
>>> res.apply_summary
{'add': 6, 'change': 0, 'remove': 0, 'operation': 'apply'}
>>> res.outputs
{"admin": "sad", ...}
>>> res.errors
[]
>>> tf.status
<TFStatus.APPLIED: 2>

>>> tf.is_applied
True

# terraform state list
>>> res = tf.get_state_list()
>>> res.is_ok
True
>>> res.resources
['data.grid_gateway_domain.domain', 'grid_deployment.nodes', 'grid_name_proxy.p1', 'grid_network.ownnet', 'grid_scheduler.sched', 'random_password.password', 'random_string.random']


# terraform show
>>> res = tf.show()
>>> res.is_ok
True
>>> res.json
{'format_version': '1.0', 'terraform_version': '1.1.4', 'values': {'outputs': {'admin_passwords': {'sensitive': True, 'value': 'Par12}V3'}, 'fqdn': {'sensitive': False, 'value': 'owncloudsamehabouelsaad.gent01.dev.grid.tf'}, 'nodes_ip': {'sensitive': False, 'value': '10.1.3.2'}, 'nodes_ygg_ip': {'sensitive': False, 'value': '301:a9bd:9b77:ce71:399e:1bab:7483:12c3'}}, 'root_module': {'resources': [{'address': 'data.grid_gateway_domain.domain', 'mode': 'data', 'type': 'grid_gateway_domain', 'name': 'domain', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'fqdn': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'id': '1643756147', 'name': 'owncloudsamehabouelsaad', 'node': 7}, 'sensitive_values': {}}, {'address': 'grid_deployment.nodes', 'mode': 'managed', 'type': 'grid_deployment', 'name': 'nodes', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'disks': [{'description': 'volume holding docker data', 'name': 'data_samehabouelsaad', 'size': 70}], 'id': '6799', 'ip_range': '10.1.3.0/24', 'network_name': 'network_samehabouelsaad', 'node': 17, 'qsfs': [], 'vms': [{'computedip': '', 'computedip6': '', 'cpu': 4, 'description': '', 'entrypoint': '/sbin/zinit init', 'env_vars': {'OWNCLOUD_ADMIN_PASSWORD': 'Par12}V3', 'OWNCLOUD_ADMIN_USERNAME': 'admin', 'OWNCLOUD_DOMAIN': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'OWNCLOUD_MAIL_DOMAIN': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'OWNCLOUD_MAIL_FROM_ADDRESS': 'owncloud', 'OWNCLOUD_MAIL_SMTP_HOST': '', 'OWNCLOUD_MAIL_SMTP_NAME': '', 'OWNCLOUD_MAIL_SMTP_PASSWORD': '', 'OWNCLOUD_MAIL_SMTP_PORT': '', 'OWNCLOUD_MAIL_SMTP_SECURE': 'none', 'SSH_KEY': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC9MI7fh4xEOOEKL7PvLvXmSeRWesToj6E26bbDASvlZnyzlSKFLuYRpnVjkr8JcuWKZP6RQn8+2aRs6Owyx7Tx+9kmEh7WI5fol0JNDn1D0gjp4XtGnqnON7d0d5oFI+EjQQwgCZwvg0PnV/2DYoH4GJ6KPCclPz4a6eXrblCLA2CHTzghDgyj2x5B4vB3rtoI/GAYYNqxB7REngOG6hct8vdtSndeY1sxuRoBnophf7MPHklRQ6EG2GxQVzAOsBgGHWSJPsXQkxbs8am0C9uEDL+BJuSyFbc/fSRKptU1UmS18kdEjRgGNoQD7D+Maxh1EbmudYqKW92TVgdxXWTQv1b1+3dG5+9g+hIWkbKZCBcfMe4nA5H7qerLvoFWLl6dKhayt1xx5mv8XhXCpEC22/XHxhRBHBaWwSSI+QPOCvs4cdrn4sQU+EXsy7+T7FIXPeWiC2jhFd6j8WIHAv6/rRPsiwV1dobzZOrCxTOnrqPB+756t7ANxuktsVlAZaM= sameh@sameh-inspiron-3576'}, 'flist': 'https://hub.grid.tf/samehabouelsaad.3bot/abouelsaad-owncloud-10.9.1.flist', 'flist_checksum': '', 'ip': '10.1.3.2', 'memory': 4096, 'mounts': [{'disk_name': 'data_samehabouelsaad', 'mount_point': '/var/lib/docker'}], 'name': 'owncloud_samehabouelsaad', 'planetary': True, 'publicip': False, 'publicip6': False, 'rootfs_size': 0, 'ygg_ip': '301:a9bd:9b77:ce71:399e:1bab:7483:12c3'}], 'zdbs': []}, 'sensitive_values': {'disks': [{}], 'qsfs': [], 'vms': [{'env_vars': {'OWNCLOUD_ADMIN_PASSWORD': True}, 'mounts': [{}]}], 'zdbs': []}, 'depends_on': ['data.grid_gateway_domain.domain', 'grid_network.ownnet', 'grid_scheduler.sched', 'random_password.password']}, {'address': 'grid_name_proxy.p1', 'mode': 'managed', 'type': 'grid_name_proxy', 'name': 'p1', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'backends': ['http://301:a9bd:9b77:ce71:399e:1bab:7483:12c3:80'], 'description': None, 'fqdn': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'id': '7aaebb59-1710-419c-b166-88c8e1820815', 'name': 'owncloudsamehabouelsaad', 'name_contract_id': 6800, 'node': 7, 'node_deployment_id': {'7': 6801}, 'tls_passthrough': False}, 'sensitive_values': {'backends': [False], 'node_deployment_id': {}}, 'depends_on': ['data.grid_gateway_domain.domain', 'grid_deployment.nodes', 'grid_network.ownnet', 'grid_scheduler.sched', 'random_password.password']}, {'address': 'grid_network.ownnet', 'mode': 'managed', 'type': 'grid_network', 'name': 'ownnet', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'access_wg_config': '\n[Interface]\nAddress = 100.64.1.2\nPrivateKey = 6PaE0fIZEtiFbTOVpYp4aJ4EoUciPOTs7fjronC82HM=\n[Peer]\nPublicKey = uRyYR2PID/Qtdg8rQYBWanUQofiZISI19buSyP9PfHY=\nAllowedIPs = 10.1.0.0/16, 100.64.0.0/16\nPersistentKeepalive = 25\nEndpoint = 185.206.122.32:4746\n\t', 'add_wg_access': True, 'description': 'server network', 'external_ip': '10.1.2.0/24', 'external_sk': '6PaE0fIZEtiFbTOVpYp4aJ4EoUciPOTs7fjronC82HM=', 'id': 'e76eb098-7de7-4dab-958e-1fd55ee74d25', 'ip_range': '10.1.0.0/16', 'name': 'network_samehabouelsaad', 'node_deployment_id': {'17': 6797, '8': 6798}, 'nodes': [17], 'nodes_ip_range': {'17': '10.1.3.0/24', '8': '10.1.4.0/24'}, 'public_node_id': 8}, 'sensitive_values': {'node_deployment_id': {}, 'nodes': [False], 'nodes_ip_range': {}}, 'depends_on': ['grid_scheduler.sched']}, {'address': 'grid_scheduler.sched', 'mode': 'managed', 'type': 'grid_scheduler', 'name': 'sched', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'id': '1643755862', 'nodes': {'name_samehabouelsaad': 7, 'server_samehabouelsaad': 17}, 'requests': [{'certified': False, 'cru': 2, 'domain': False, 'farm': '', 'hru': 0, 'ipv4': False, 'mru': 8096, 'name': 'server_samehabouelsaad', 'sru': 151200}, {'certified': False, 'cru': 0, 'domain': True, 'farm': '', 'hru': 0, 'ipv4': False, 'mru': 0, 'name': 'name_samehabouelsaad', 'sru': 0}]}, 'sensitive_values': {'nodes': {}, 'requests': [{}, {}]}}, {'address': 'random_password.password', 'mode': 'managed', 'type': 'random_password', 'name': 'password', 'provider_name': 'registry.terraform.io/hashicorp/random', 'schema_version': 0, 'values': {'id': 'none', 'keepers': None, 'length': 8, 'lower': True, 'min_lower': 0, 'min_numeric': 0, 'min_special': 0, 'min_upper': 0, 'number': True, 'override_special': None, 'result': 'Par12}V3', 'special': True, 'upper': True}, 'sensitive_values': {}}, {'address': 'random_string.random', 'mode': 'managed', 'type': 'random_string', 'name': 'random', 'provider_name': 'registry.terraform.io/hashicorp/random', 'schema_version': 1, 'values': {'id': '1f902u', 'keepers': None, 'length': 6, 'lower': True, 'min_lower': 0, 'min_numeric': 0, 'min_special': 0, 'min_upper': 0, 'number': True, 'override_special': None, 'result': '1f902u', 'special': False, 'upper': False}, 'sensitive_values': {}}]}}}


>>> res = tf.destroy(vars={"user": tf.instance_name})
>>> res.is_ok
True
res.destroy_summary
[{'add': 0, 'change': 0, 'remove': 6, 'operation': 'destroy'}]

>>> tf.status
<TFStatus.DESTROYED: 3>

# terraform destroy
>>> tf.is_destroyed
True

# delete state dir, works if no resources exists in the state
>>> tf._clean_state_dir()
True
```

"""
from jumpscale.core.base import Base, fields
from jumpscale.core.exceptions import NotFound, Runtime

import subprocess
import json
import os
import shutil
from jumpscale.loader import j
from enum import Enum, auto

TF_BINARY = "terraform"
# although it is not the client responsibility to provide this paths,
# it provides a default values for plugin_dir, and state_dir that user can override.
ROOT_PATH = os.path.join(os.path.expanduser("~"), "tf_data")
PLUGIN_DIR = os.path.join(ROOT_PATH, "tf_plugins")
STATES_DIR = os.path.join(ROOT_PATH, "tf_states")

SHOW_TF_COMMAND_OUTPUT = os.environ.get("TF_CLIENT_DEBUG", False) == "True"

_GLOBAL_ARGS = {
    "chdir": "-chdir={0}",
}
_AUTOMATION_ARGS = {
    "no-input": "-input=false",
    "no-color": "-no-color",
}
_APPLY_ARGS = {
    "parallelism": "-parallelism=1",
    "auto-approve": "-auto-approve",
    "json": "-json",
}
_INIT_ARGS = {
    "upgrade": "-upgrade",
    "from-module": "-from-module={0}",
}
_OUTPUT_ARGS = {
    "json": "-json",
    "no-color": "-no-color",
}


class TFStatus(Enum):
    """it is just a enum to represent the status of last call to apply/destroy commands for a terraform instance."""

    # initial state
    CREATED = auto()
    # terraform apply command was called and succeeded
    APPLIED = auto()
    # terraform destroy command was called and succeeded
    DESTROYED = auto()
    # terraform apply command was called and failed
    FAILED_TO_APPLY = auto()
    # terraform destroy command was called and failed
    FAILED_TO_DESTROY = auto()


class TFResult:
    """Object representing the result of a terraform command."""

    def __init__(self, rc, json_messages=None, text=None):
        """
        Args:
            rc (int): the return code of the command.
            json_messages (list[dict], optional): the json messages of the command.
            text (string, optional): the text output of the command, if command has no json output
        """
        self.rc = rc
        self.json = json_messages
        self.text = text
        self.resources = []

    def __repr__(self):
        return f"<TFResult: rc={self.rc}>"

    def __get_summary(self, operation):
        """return the summary of the operation in the apply/destroy/plan messages

        Args:
            operation (string): the operation name.

        Returns:
            dict: the summary of the operation.
        """
        messages = self.parse_messages(type="change_summary", key="changes")
        if not messages:
            return {}
        for message in messages:
            if message["operation"] == operation:
                return message
        return {}

    def parse_messages(self, type, level=None, key=None):
        """Parse terraform messages to get a specific messages/message or values/value. \
            see: https://www.terraform.io/internals/machine-readable-ui for info about messages structure.
        Args:
            type (string): ex. "change_summary", "apply_complete", "diagnostic", ...
            level (string, optional): ex, "error", "warning", 'info", ...
            key (string, optional):  ex, "@message", "changes", 'outputs", ...

        Returns:
            list[dict]: represents the filtered command output messages
        
        Example:
            >>> tf = j.tools.terraform.get("samehabouelsaad")
            >>> res = tf.plan(vars={"user": "abouelsaad"})
            >>> res.prase_messages(type="change_summary", key="changes")
            [{'add': 0, 'change': 0, 'remove': 0, 'operation': 'plan'}]
        """
        if not self.json:
            return []
        filtered_messages = [
            message
            for message in self.json
            if message["type"] == type and (level == None or message["@level"] == level)
        ]  # filter messages by type and level
        if key:
            values = [message[key] for message in filtered_messages if message.get(key)]
            return values
        return filtered_messages

    @property
    def is_ok(self):
        """Return True if the command exited with success, False otherwise."""
        return self.rc == 0 or self.rc == 2

    @property
    def errors(self):
        """Return a list of errors from the command output."""
        return self.parse_messages(type="diagnostic", level="error", key="@message")

    @property
    def outputs(self):
        """Return a dict of outputs from the command output or apply."""
        outputs = self.parse_messages(type="outputs", key="outputs")
        outputs_dict = {}
        for output in outputs:
            outputs_dict.update(
                {
                    key: value.get("value")
                    for key, value in output.items()
                    if value.get("value")
                }
            )
        return outputs_dict

    @property
    def plan_summary(self):
        """Return a dict of the plan summary from the command plan/apply/destroy."""
        return self.__get_summary("plan")

    @property
    def apply_summary(self):
        """Return a dict of the plan summary from the command apply."""
        return self.__get_summary("apply")

    @property
    def destroy_summary(self):
        """Return a dict of the destroy summary from the command destroy."""
        return self.__get_summary("destroy")

    @property
    def changes_present(self):
        """Return True if the command plan contains changes for remote state, False otherwise."""
        if self.plan_summary:
            return (
                self.plan_summary.get("add") > 0 or self.plan_summary.get("change") > 0 or self.plan_summary.get("remove") > 0
            )
        return False

    @property
    def last_error(self):
        """Return the last error from the command output."""
        if self.errors:
            return self.errors[-1]
        elif self.text and not self.is_ok:
            return self.text
        else:
            return ""


class Terraform(Base):
    """Object representing a terraform instance."""

    _initialized = (
        fields.Boolean()
    )  # if the state_dir is at least initialized once, not indicating if it need to be initialized again
    extra_env = fields.Typed(dict, default={})
    state_dir = fields.String()  # the directory where the terraform state is stored
    plugin_dir = (
        fields.String()
    )  # the directory where the terraform plugins are downloaded
    source_module = (
        fields.String()
    )  # the source module to use for the terraform init command
    status = fields.Enum(
        TFStatus
    )  # the status of the last call to apply/destroy commands

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_install(TF_BINARY)
        self._env = None
        if not self.state_dir:
            self.state_dir = os.path.join(STATES_DIR, self.instance_name)
        if not self.plugin_dir:
            self.plugin_dir = PLUGIN_DIR

    @staticmethod
    def _check_install(binary):
        """Check if the binary is installed.

        Args:
            binary (string): binary name

        Raises:
            NotFound: if binary not installed
        """
        if subprocess.call(["which", binary], stdout=subprocess.DEVNULL):
            raise NotFound(f"{binary} not installed")

    @property
    def is_initialized(self):
        """Check if the tf instance is initialized.

        Returns:
            bool: True if the instance is initialized using the client, False otherwise.
        """
        return self._initialized

    @property
    def is_applied(self):
        """Check if the tf instance is applied.

        Returns:
            bool: True if the instance is applied using the client, False otherwise.
        """
        return self.status == TFStatus.APPLIED

    @property
    def is_destroyed(self):
        """Check if the tf instance is destroyed.

        Returns:
            bool: True if the instance is destroyed using the client, False otherwise.
        """
        return self.status == TFStatus.DESTROYED

    @property
    def is_errored(self):
        """Check if the tf instance has error during last apply or destroy operation.

        Returns:
            bool: True if the client's last apply or destroy operation was unscusseded, False otherwise.
        """
        return self.status in [TFStatus.FAILED_TO_APPLY, TFStatus.FAILED_TO_DESTROY]

    @property
    def env(self):
        """get user’s environmental variable and update it with the extra_env.

        Returns:
            dict: mapping object that represents the environment variables to be used by the terraform command.
        """
        self.validate()
        self._env = os.environ.copy()
        self._env.update(**self.extra_env)
        return self._env

    def _run_cmd(self, cmd, check=False):
        """Run a terraform command.

        Args:
            cmd (list[string]): sub-command and its args to run
            check (bool, optional): raise exception when the command exited with error. Defaults to False.

        Raises:
            Runtime: if check is True and the command exited with error.

        Returns:
            subprocess.Popen: object containe the output of the command and the exit code.
        """
        full_cmd = [TF_BINARY, _GLOBAL_ARGS["chdir"].format(self.state_dir), *cmd]
        j.logger.info(f"Running command: {full_cmd}")
        proc = subprocess.run(
            full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env
        )
        if check and proc.returncode:
            raise Runtime(
                f"terraform command failed with {proc.stdout.decode()}/n {proc.stderr.decode()}"
            )
        return proc

    def _clean_state_dir(self, force=False):
        """remove the state dir for the instance if exists

        Args:
            force (bool, optional): if True, the state dir will be removed even if there re resources in the state list. Defaults to False.

        Return:
            bool: True if the state dir was removed or not exists, False otherwise.
        """
        if os.path.exists(self.state_dir):
            if force or (self.get_state_list().resources == []):
                shutil.rmtree(self.state_dir)
                j.logger.info(
                    f"the state dir '{self.state_dir}' of the instance '{self.instance_name}' was removed."
                )
            else:
                j.logger.warning(
                    f"the state dir '{self.state_dir}' of the instance '{self.instance_name}' is not empty. use force=True to remove it."
                )
                return False
        else:
            j.logger.warning(
                f"the state dir of the instance '{self.instance_name}' is not exists. skipping."
            )
        return True

    def _log_proc_output(self, proc):
        """Log the output of a subprocess.

        Args:
            proc (subprocess.Popen): object containe the output of the command and the exit code.
        """
        if SHOW_TF_COMMAND_OUTPUT:
            j.logger.debug(f"STDOUT:\n{proc.stdout.decode()}")
            if proc.stderr:
                j.logger.debug(f"STDERR:\n{proc.stderr.decode()}")
            j.logger.debug(f"EXIT CODE: {proc.returncode}")

    def copy_source_module(self):
        """copy the configuration files from instance source_module to instance state dir.

        Raises:
            FileNotFoundError: if the source_module is not set or exists.
        """
        if not self.source_module:
            raise FileNotFoundError("source_module is not set")
        if not os.path.exists(self.source_module):
            raise FileNotFoundError(
                f"the source directory '{self.source_module}' does not exist."
            )

        # copy recursively all files and directories
        shutil.copytree(self.source_module, self.state_dir, dirs_exist_ok=True)

    def providers_mirror(self):
        """automatically populate instance plugin_dir directory that will be used as a local filesystem mirror for the required providers.

        Returns:
            TFResult: result object of the operation.
        """
        target_dir = self.plugin_dir
        cmd = ["providers", "mirror", target_dir]
        # use _run_cmd to call the command and return the exite code and the output
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            j.logger.info(f"terraform providers mirror succeeded. path: {target_dir}")
        else:
            j.logger.error(f"terraform providers mirror failed. path: {target_dir}")
        return TFResult(
            rc=proc.returncode, text=proc.stdout.decode() or proc.stderr.decode()
        )

    def init(self, upgrade=False, use_plugin_dir=False, from_module=False):
        """initialize a working directory containing Terraform configuration files. \
            if succeeded, the instance status will be set to INITIALIZED.
        more info: https://www.terraform.io/cli/commands/init

        Args:
            upgrade (bool, optional): Opt to upgrade modules and plugins as part of their respective installation steps. Defaults to False.
            use_plugin_dir (bool, optional): Force plugin installation to read plugins only from {PLUGIN_DIR} \
                this optionally making plugins available locally to avoid repeated re-installation. Defaults to False.
            from_module (bool, optional): copy the configuration files (natively using terraform init command) from instance source_module to instance state dir. Defaults to False.

        Returns:
            int: command exit code
        """
        cmd = ["init"]
        if upgrade:
            cmd.append(_INIT_ARGS["upgrade"])
        if use_plugin_dir:
            cmd.append(f"-plugin-dir={self.plugin_dir}")
        if from_module:
            cmd.append(_INIT_ARGS["from-module"].format(self.source_module))
            # create state dir if not exists
            os.makedirs(self.state_dir, exist_ok=True)
        cmd.extend(_AUTOMATION_ARGS.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            self._initialized = True
            self.save()
            j.logger.info(
                f"terraform init for the deployment instance '{self.instance_name}' succeeded."
            )
        else:
            j.logger.error(
                f"terraform init for the deployment instance '{self.instance_name}' failed."
            )
        return TFResult(
            rc=proc.returncode, text=proc.stdout.decode() or proc.stderr.decode()
        )

    def apply(self, vars=None):
        """create a new execution plan then apply the changes in the plan. set the instance status to APPLIED or FAILED_TO_APPLY.

        Args:
            vars (dict, optional): dict of the values for input variables declared in your root module. Defaults to None.

        Returns:
            TFResult: result object of the operation.
        """
        cmd = ["apply"]
        if vars:
            # apply -var for every key value pair
            for key, value in vars.items():
                cmd.append(f"-var={key}={value}")
        cmd.extend(_AUTOMATION_ARGS.values())
        cmd.extend(_APPLY_ARGS.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        messages = list(map(json.loads, proc.stdout.decode().splitlines()))
        if proc.returncode == 0:
            self.status = TFStatus.APPLIED
            j.logger.info(
                f"the planned changes for the deployment instance '{self.instance_name}' were applied successfully."
            )
        else:
            self.status = TFStatus.FAILED_TO_APPLY
            j.logger.error(
                f"the planned changes for the deployment instance '{self.instance_name}' were failed to apply."
            )
        self.save()
        result = TFResult(rc=proc.returncode, json_messages=messages)
        if proc.stderr:
            result.text = proc.stderr.decode()
        return result

    def destroy(self, vars=None):
        """Destroy the terraform managed infrastructure. set the instance status to DESTROYED or FAILED_TO_DESTROY.

        Args:
            vars (dict, optional): dict of the values for input variables declared in your root module. Defaults to None.

        Returns:
            TFResult: result object of the operation.
        """
        cmd = ["destroy"]
        if vars:
            # apply -var for every key value pair
            for key, value in vars.items():
                cmd.append(f"-var={key}={value}")
        cmd.extend(_AUTOMATION_ARGS.values())
        cmd.extend(_APPLY_ARGS.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        messages = list(map(json.loads, proc.stdout.decode().splitlines()))
        if proc.returncode == 0:
            self.status = TFStatus.DESTROYED
            j.logger.info(
                f"the deployment instance '{self.instance_name}' was destroyed successfully."
            )
        else:
            self.status = TFStatus.FAILED_TO_DESTROY
            j.logger.error(
                f"the deployment instance '{self.instance_name}' was failed to destroy."
            )
        self.save()

        return TFResult(rc=proc.returncode, json_messages=messages)

    def get_state_list(self, filter_by_resource=None, filter_by_id=None):
        """list resources within a Terraform state. If no filter/address are given, all resources are listed.

        Args:
            filter_by_resource (string, optional): resource address. Defaults to None.
            filter_by_id (string, optional): resource id. Defaults to None.

        Returns:
            TFResult: result object of the operation. you can access the result.resources to get the list of resources.
        """
        cmd = ["state", "list"]
        if filter_by_id:
            cmd.append(f"-id={filter_by_id}")
        elif filter_by_resource:
            cmd.append(f"{filter_by_resource}")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        result = TFResult(
            rc=proc.returncode, text=proc.stdout.decode() or proc.stderr.decode()
        )
        result.resources.extend(proc.stdout.decode().splitlines())
        return result

    def get_output(self):
        """return the output values exported by a terraform module.

        Returns:
            TFResult: result object of the operation. you can access the result.outputs to get the dict of outputs.
        """
        cmd = ["output"]
        cmd.extend(_OUTPUT_ARGS.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            output = json.loads(proc.stdout.decode())
            return TFResult(
                rc=proc.returncode,
                json_messages=[{"type": "outputs", "outputs": output}],
            )

        return TFResult(
            rc=proc.returncode, text=proc.stdout.decode() or proc.stderr.decode()
        )

    def validate_hcl(self):
        """Validate the .tf files in the state dir of the instance.
            see: https://www.terraform.io/docs/commands/validate

        Returns:
            TFResult: result object of the operation. you can access the result.json result.

        Example:
            >>> result = instance.validate_hcl()
            >>> res.json
            {
                "format_version": "1.0",
                "valid": true,
                "error_count": 0,
                "warning_count": 0,
                "diagnostics": []
            }
        """
        cmd = ["validate"]
        cmd.extend(_OUTPUT_ARGS.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        try:
            output = json.loads(proc.stdout.decode())
            result = TFResult(rc=proc.returncode, json_messages=output)
        except json.decoder.JSONDecodeError:
            output = proc.stdout.decode() or proc.stderr.decode()
            result = TFResult(rc=proc.returncode, text=output)
        return result

    def show(self):
        """Show the terraform managed infrastructure state.

        Returns:
            TFResult: result object of the operation. you can access the result.json result.
        """
        cmd = ["show"]
        cmd.extend(_OUTPUT_ARGS.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        try:
            output = json.loads(proc.stdout.decode())
            result = TFResult(rc=proc.returncode, json_messages=output)

        except json.decoder.JSONDecodeError:
            output = proc.stdout.decode() or proc.stderr.decode()
            result = TFResult(rc=proc.returncode, text=output)
        return result

    def plan(self, vars=None):
        """creates unpersistence execution plan for the underlying terraform managed infrastructure.

        Args:
            vars (dict, optional): dict of the values for input variables declared in your root module. Defaults to None.

        Returns:
            TFResult: result object of the operation. you can access the result.changes_present to know if there are any changes required to remote state to match the instance configuration files
            also you can access result.plan_summary for an overview.
        """
        cmd = ["plan"]
        if vars:
            for key, value in vars.items():
                cmd.append(f"-var={key}={value}")
        cmd.extend(_OUTPUT_ARGS.values())
        cmd.append("-detailed-exitcode")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return TFResult(
            rc=proc.returncode,
            json_messages=list(map(json.loads, proc.stdout.decode().splitlines())),
        )

    # TODO: add workspace support
