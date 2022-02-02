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

also you could set any provider specific input variables in environment variables.

## Usage

### Basic usage

```python
# get new instance of terraform
>>> tf = j.tools.terraform.get("samehabouelsaad")
# optionally specify extra environment variables to be set for terraform command.
>>> instance.extra_env = {'MNEMONICS': 'mnemonics',
                      'NETWROK': 'test'}
>>> tf.save()
# create the instance's state dir and set the content of the main.tf file
>>> tf.hcl_content = "should be a valid .tf file content"

>>> tf.status
<TFStatus.CREATED: 1>

# terraform providers mirror, populate the PLUGIN_DIR with the required terraform plugins
>>> tf.providers_mirror()
(0, '- Mirroring threefoldtech/grid...\n  - Selected v0.1.23 with no constraints\n  - Downloading package for linux_amd64...\n  - Package authenticated: self-signed\n- Mirroring hashicorp/random...\n  - Selected v3.1.0 with no constraints\n  - Downloading package for linux_amd64...\n  - Package authenticated: signed by HashiCorp\n')

# terraform init 
>>> tf.init(use_plugin_dir=True)
0

>>> tf.is_initialized
True

# terrafrom validate, check if the .tf file is valid
>>> tf.validate_hcl()
(0, {'format_version': '1.0', 'valid': True, 'error_count': 0, 'warning_count': 0, 'diagnostics': []})

# terrafrom apply
>>> tf.apply(vars={'user': 'samehabouelsaad'})
(0, [
    {'@level': 'info', '@message': 'Terraform 1.1.4', '@module': 'terraform.ui', '@timestamp': '2022-02-02T00:55:18.948737+02:00', 'terraform': '1.1.4', 'type': 'version', 'ui': '1.0'},
    {'@level': 'info', '@message': 'random_password.password: Refreshing state... [id=none]', '@module': 'terraform.ui', '@timestamp': '2022-02-02T00:55:37.969492+02:00', 'hook': {'resource': {'addr': 'random_password.password', 'module': '', 'resource': 'random_password.password', 'implied_provider': 'random', 'resource_type': 'random_password', 'resource_name': 'password', 'resource_key': None}, 'id_key': 'id', 'id_value': 'none'}, 'type': 'refresh_start'},
    {'@level': 'info', '@message': 'random_password.password: Refresh complete [id=none]', '@module': 'terraform.ui', '@timestamp': '2022-02-02T00:55:37.973426+02:00', 'hook': {'resource': {'addr': 'random_password.password', 'module': '', 'resource': 'random_password.password', 'implied_provider': 'random', 'resource_type': 'random_password', 'resource_name': 'password', 'resource_key': None}, 'id_key': 'id', 'id_value': 'none'}, 'type': 'refresh_complete'},
    {'@level': 'info', '@message': 'random_string.random: Refreshing state... [id=1f902u]', '@module': 'terraform.ui', '@timestamp': '2022-02-02T00:55:37.983823+02:00', 'hook': {'resource': {'addr': 'random_string.random', 'module': '', 'resource': 'random_string.random', 'implied_provider': 'random', 'resource_type': 'random_string', 'resource_name': 'random', 'resource_key': None}, 'id_key': 'id', 'id_value': '1f902u'}, 'type': 'refresh_start'},
    ...........
    {'@level': 'info', '@message': 'grid_name_proxy.p1: Still creating... [1m0s elapsed]', '@module': 'terraform.ui', '@timestamp': '2022-02-02T01:00:18.075577+02:00', 'hook': {'resource': {'addr': 'grid_name_proxy.p1', 'module': '', 'resource': 'grid_name_proxy.p1', 'implied_provider': 'grid', 'resource_type': 'grid_name_proxy', 'resource_name': 'p1', 'resource_key': None}, 'action': 'create', 'elapsed_seconds': 60}, 'type': 'apply_progress'},
    {'@level': 'info', '@message': 'grid_name_proxy.p1: Creation complete after 1m7s [id=7aaebb59-1710-419c-b166-88c8e1820815]', '@module': 'terraform.ui', '@timestamp': '2022-02-02T01:00:24.955846+02:00', 'hook': {'resource': {'addr': 'grid_name_proxy.p1', 'module': '', 'resource': 'grid_name_proxy.p1', 'implied_provider': 'grid', 'resource_type': 'grid_name_proxy', 'resource_name': 'p1', 'resource_key': None}, 'action': 'create', 'id_key': 'id', 'id_value': '7aaebb59-1710-419c-b166-88c8e1820815', 'elapsed_seconds': 67}, 'type': 'apply_complete'},
    {'@level': 'info', '@message': 'Apply complete! Resources: 3 added, 0 changed, 0 destroyed.', '@module': 'terraform.ui', '@timestamp': '2022-02-02T01:00:24.971786+02:00', 'changes': {'add': 3, 'change': 0, 'remove': 0, 'operation': 'apply'}, 'type': 'change_summary'},
    {'@level': 'info', '@message': 'Outputs: 4', '@module': 'terraform.ui', '@timestamp': '2022-02-02T01:00:24.971880+02:00', 'outputs': {'admin_passwords': {'sensitive': True, 'type': 'string', 'value': 'Par12}V3'}, 'fqdn': {'sensitive': False, 'type': 'string', 'value': 'owncloudsamehabouelsaad.gent01.dev.grid.tf'}, 'nodes_ip': {'sensitive': False, 'type': 'string', 'value': '10.1.3.2'}, 'nodes_ygg_ip': {'sensitive': False, 'type': 'string', 'value': '301:a9bd:9b77:ce71:399e:1bab:7483:12c3'}}, 'type': 'outputs'}])

>>> tf.status                                                                                                                                                                                           
<TFStatus.APPLIED: 2>

>>> tf.is_applied
True

>>> tf.state_dir                                                                                                                                                                                        
'/home/sameh/tf_owncloud/tf_states/samehabouelsaad'

# terraform state list
>>> tf.get_state_list() 
(0, ['data.grid_gateway_domain.domain', 'grid_deployment.nodes', 'grid_name_proxy.p1', 'grid_network.ownnet', 'grid_scheduler.sched', 'random_password.password', 'random_string.random'])

# terrafomt output 
>>> tf.get_output("fqdn") 
(0, 'owncloudsamehabouelsaad.gent01.dev.grid.tf')

>>> tf.get_plan_summary(vars={"user": tf.instance_name})
(0, {'add': 0, 'change': 0, 'remove': 0, 'operation': 'plan'})

# terrafomr show
>>> tf.show()
(0, {'format_version': '1.0', 'terraform_version': '1.1.4', 'values': {'outputs': {'admin_passwords': {'sensitive': True, 'value': 'Par12}V3'}, 'fqdn': {'sensitive': False, 'value': 'owncloudsamehabouelsaad.gent01.dev.grid.tf'}, 'nodes_ip': {'sensitive': False, 'value': '10.1.3.2'}, 'nodes_ygg_ip': {'sensitive': False, 'value': '301:a9bd:9b77:ce71:399e:1bab:7483:12c3'}}, 'root_module': {'resources': [{'address': 'data.grid_gateway_domain.domain', 'mode': 'data', 'type': 'grid_gateway_domain', 'name': 'domain', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'fqdn': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'id': '1643756147', 'name': 'owncloudsamehabouelsaad', 'node': 7}, 'sensitive_values': {}}, {'address': 'grid_deployment.nodes', 'mode': 'managed', 'type': 'grid_deployment', 'name': 'nodes', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'disks': [{'description': 'volume holding docker data', 'name': 'data_samehabouelsaad', 'size': 70}], 'id': '6799', 'ip_range': '10.1.3.0/24', 'network_name': 'network_samehabouelsaad', 'node': 17, 'qsfs': [], 'vms': [{'computedip': '', 'computedip6': '', 'cpu': 4, 'description': '', 'entrypoint': '/sbin/zinit init', 'env_vars': {'OWNCLOUD_ADMIN_PASSWORD': 'Par12}V3', 'OWNCLOUD_ADMIN_USERNAME': 'admin', 'OWNCLOUD_DOMAIN': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'OWNCLOUD_MAIL_DOMAIN': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'OWNCLOUD_MAIL_FROM_ADDRESS': 'owncloud', 'OWNCLOUD_MAIL_SMTP_HOST': '', 'OWNCLOUD_MAIL_SMTP_NAME': '', 'OWNCLOUD_MAIL_SMTP_PASSWORD': '', 'OWNCLOUD_MAIL_SMTP_PORT': '', 'OWNCLOUD_MAIL_SMTP_SECURE': 'none', 'SSH_KEY': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC9MI7fh4xEOOEKL7PvLvXmSeRWesToj6E26bbDASvlZnyzlSKFLuYRpnVjkr8JcuWKZP6RQn8+2aRs6Owyx7Tx+9kmEh7WI5fol0JNDn1D0gjp4XtGnqnON7d0d5oFI+EjQQwgCZwvg0PnV/2DYoH4GJ6KPCclPz4a6eXrblCLA2CHTzghDgyj2x5B4vB3rtoI/GAYYNqxB7REngOG6hct8vdtSndeY1sxuRoBnophf7MPHklRQ6EG2GxQVzAOsBgGHWSJPsXQkxbs8am0C9uEDL+BJuSyFbc/fSRKptU1UmS18kdEjRgGNoQD7D+Maxh1EbmudYqKW92TVgdxXWTQv1b1+3dG5+9g+hIWkbKZCBcfMe4nA5H7qerLvoFWLl6dKhayt1xx5mv8XhXCpEC22/XHxhRBHBaWwSSI+QPOCvs4cdrn4sQU+EXsy7+T7FIXPeWiC2jhFd6j8WIHAv6/rRPsiwV1dobzZOrCxTOnrqPB+756t7ANxuktsVlAZaM= sameh@sameh-inspiron-3576'}, 'flist': 'https://hub.grid.tf/samehabouelsaad.3bot/abouelsaad-owncloud-10.9.1.flist', 'flist_checksum': '', 'ip': '10.1.3.2', 'memory': 4096, 'mounts': [{'disk_name': 'data_samehabouelsaad', 'mount_point': '/var/lib/docker'}], 'name': 'owncloud_samehabouelsaad', 'planetary': True, 'publicip': False, 'publicip6': False, 'rootfs_size': 0, 'ygg_ip': '301:a9bd:9b77:ce71:399e:1bab:7483:12c3'}], 'zdbs': []}, 'sensitive_values': {'disks': [{}], 'qsfs': [], 'vms': [{'env_vars': {'OWNCLOUD_ADMIN_PASSWORD': True}, 'mounts': [{}]}], 'zdbs': []}, 'depends_on': ['data.grid_gateway_domain.domain', 'grid_network.ownnet', 'grid_scheduler.sched', 'random_password.password']}, {'address': 'grid_name_proxy.p1', 'mode': 'managed', 'type': 'grid_name_proxy', 'name': 'p1', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'backends': ['http://301:a9bd:9b77:ce71:399e:1bab:7483:12c3:80'], 'description': None, 'fqdn': 'owncloudsamehabouelsaad.gent01.dev.grid.tf', 'id': '7aaebb59-1710-419c-b166-88c8e1820815', 'name': 'owncloudsamehabouelsaad', 'name_contract_id': 6800, 'node': 7, 'node_deployment_id': {'7': 6801}, 'tls_passthrough': False}, 'sensitive_values': {'backends': [False], 'node_deployment_id': {}}, 'depends_on': ['data.grid_gateway_domain.domain', 'grid_deployment.nodes', 'grid_network.ownnet', 'grid_scheduler.sched', 'random_password.password']}, {'address': 'grid_network.ownnet', 'mode': 'managed', 'type': 'grid_network', 'name': 'ownnet', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'access_wg_config': '\n[Interface]\nAddress = 100.64.1.2\nPrivateKey = 6PaE0fIZEtiFbTOVpYp4aJ4EoUciPOTs7fjronC82HM=\n[Peer]\nPublicKey = uRyYR2PID/Qtdg8rQYBWanUQofiZISI19buSyP9PfHY=\nAllowedIPs = 10.1.0.0/16, 100.64.0.0/16\nPersistentKeepalive = 25\nEndpoint = 185.206.122.32:4746\n\t', 'add_wg_access': True, 'description': 'server network', 'external_ip': '10.1.2.0/24', 'external_sk': '6PaE0fIZEtiFbTOVpYp4aJ4EoUciPOTs7fjronC82HM=', 'id': 'e76eb098-7de7-4dab-958e-1fd55ee74d25', 'ip_range': '10.1.0.0/16', 'name': 'network_samehabouelsaad', 'node_deployment_id': {'17': 6797, '8': 6798}, 'nodes': [17], 'nodes_ip_range': {'17': '10.1.3.0/24', '8': '10.1.4.0/24'}, 'public_node_id': 8}, 'sensitive_values': {'node_deployment_id': {}, 'nodes': [False], 'nodes_ip_range': {}}, 'depends_on': ['grid_scheduler.sched']}, {'address': 'grid_scheduler.sched', 'mode': 'managed', 'type': 'grid_scheduler', 'name': 'sched', 'provider_name': 'registry.terraform.io/threefoldtech/grid', 'schema_version': 0, 'values': {'id': '1643755862', 'nodes': {'name_samehabouelsaad': 7, 'server_samehabouelsaad': 17}, 'requests': [{'certified': False, 'cru': 2, 'domain': False, 'farm': '', 'hru': 0, 'ipv4': False, 'mru': 8096, 'name': 'server_samehabouelsaad', 'sru': 151200}, {'certified': False, 'cru': 0, 'domain': True, 'farm': '', 'hru': 0, 'ipv4': False, 'mru': 0, 'name': 'name_samehabouelsaad', 'sru': 0}]}, 'sensitive_values': {'nodes': {}, 'requests': [{}, {}]}}, {'address': 'random_password.password', 'mode': 'managed', 'type': 'random_password', 'name': 'password', 'provider_name': 'registry.terraform.io/hashicorp/random', 'schema_version': 0, 'values': {'id': 'none', 'keepers': None, 'length': 8, 'lower': True, 'min_lower': 0, 'min_numeric': 0, 'min_special': 0, 'min_upper': 0, 'number': True, 'override_special': None, 'result': 'Par12}V3', 'special': True, 'upper': True}, 'sensitive_values': {}}, {'address': 'random_string.random', 'mode': 'managed', 'type': 'random_string', 'name': 'random', 'provider_name': 'registry.terraform.io/hashicorp/random', 'schema_version': 1, 'values': {'id': '1f902u', 'keepers': None, 'length': 6, 'lower': True, 'min_lower': 0, 'min_numeric': 0, 'min_special': 0, 'min_upper': 0, 'number': True, 'override_special': None, 'result': '1f902u', 'special': False, 'upper': False}, 'sensitive_values': {}}]}}})

>>> rc, messages = tf.destroy(vars={"user": tf.instance_name})
>>> rc
0

>>> tf.parse_messages(messages, type="change_summary", key="changes")
[{'add': 0, 'change': 0, 'remove': 6, 'operation': 'plan'}, {'add': 0, 'change': 0, 'remove': 6, 'operation': 'destroy'}]

>>> tf.status
<TFStatus.DESTROYED: 3>

# terraform destroy
>>> tf.is_destroyed
True
```


### Listing infrastructures

"""
from jumpscale.core.base import Base, fields
from jumpscale.core.exceptions import NotFound, Runtime

import subprocess
import json
import os
from jumpscale.loader import j
from enum import Enum, auto

TF_BINARY = "terraform"
ROOT_PATH = os.path.join(os.path.expanduser("~"), "tf_owncloud")
PLUGIN_DIR = os.path.join(ROOT_PATH, "tf_plugins")
STATES_DIR = os.path.join(ROOT_PATH, "tf_states")
DEBUG = True  # os.environ.get("TF_CLIENT_DEBUG", False) == "True"

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
    "plugin-dir": f"-plugin-dir={PLUGIN_DIR}",
    "upgrade": "-upgrade",
}
_OUTPUT_ARGS = {
    "json": "-json",
    "no-color": "-no-color",
}


class TFStatus(Enum):
    CREATED = auto()
    APPLIED = auto()
    DESTROYED = auto()
    FAILED_TO_APPLY = auto()
    FAILED_TO_DESTROY = auto()


class Terraform(Base):

    extra_env = fields.Typed(dict, default={})
    _hcl_content = fields.String()
    _initialized = fields.Typed(bool, default=False)
    status = fields.Enum(TFStatus)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_install(TF_BINARY)
        self._env = None
        self._GLOBAL_ARGS = {
            "chdir": f"-chdir={self.state_dir}",
        }

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

    @staticmethod
    def parse_messages(messages, type, key=None):
        """Parse terraform messages to get a specific messages/message or values/value. \
            see: https://www.terraform.io/internals/machine-readable-ui for info about messages structure.
        Args:
            messages ([type]): [description]
            type ([type]): [description]
            key ([type], optional): [description]. Defaults to None.
            latest (bool, optional): [description]. Defaults to False.

        Returns:
            list[dict]: represents the filtered command output messages
        
        Example:
            >>> tf = j.tools.terraform.get("samehabouelsaad")
            >>> rc, messages = tf.plan(vars={"user": "abouelsaad"})
            >>> tf.prase_messages(messages, type="change_summary", key="changes")
            [{'add': 0, 'change': 0, 'remove': 0, 'operation': 'plan'}]
        """
        messages_with_type = [
            message for message in messages if message["type"] == type
        ]  # filter messages by type
        if key:
            values = [
                message[key] for message in messages_with_type if message.get(key)
            ]
            return values
        return messages_with_type

    @property
    def state_dir(self):
        """Return the path for the directory containing the .tf files for this instance.

        Returns:
            string: dir path
        """
        return os.path.join(STATES_DIR, self.instance_name)

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

    @property
    def hcl_content(self):
        """Return the content of the .tf file for this instance.

        Returns:
            string: content of the .tf file used to init this instance
        """
        return self._hcl_content

    @hcl_content.setter
    def hcl_content(self, value):
        """Create the state dir if it does not exist then write the content to main.tf.
        note: it will overwrite the main.tf file if it exists.
        this could potentially cause issues if it is not intended.

        Args:
            value (string): content of the .tf file required to create teh infrastructure
        """
        os.makedirs(self.state_dir, exist_ok=True)
        flag = "w"  # if overwrite else "x"
        filename = f"{self.state_dir}/main.tf"
        with open(filename, flag) as f:
            f.write(value)

        j.logger.info(f"hcl content saved to: {filename}")
        self._hcl_content = value
        # it may need to re-init the instance if the file contain changes that require downloading some plugins
        self._initialized = False
        self.save()

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
        full_cmd = [TF_BINARY, *self._GLOBAL_ARGS.values(), *cmd]
        j.logger.info(f"Running command: {full_cmd}")
        proc = subprocess.run(
            full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env
        )
        if check and proc.returncode:
            raise Runtime(
                f"terraform command failed with {proc.stdout.decode()}/n {proc.stderr.decode()}"
            )
        return proc

    def _log_proc_output(self, proc):
        """Log the output of a subprocess.

        Args:
            proc (subprocess.Popen): object containe the output of the command and the exit code.
        """
        if DEBUG:
            j.logger.debug(f"STDOUT:\n{proc.stdout.decode()}")
            if proc.stderr:
                j.logger.debug(f"STDERR:\n{proc.stderr.decode()}")
            j.logger.debug(f"EXIT CODE: {proc.returncode}")

    def providers_mirror(self, target_dir=PLUGIN_DIR):
        """automatically populate a directory that will be used as a local filesystem mirror for the required providers.

        Args:
            target_dir (string, optional): the target directory to mirror the providers. Defaults to PLUGIN_DIR.
        Returns:
            tuple(int, string): exit code and the output of the command.
        """
        cmd = ["providers", "mirror", target_dir]
        # use _run_cmd to call the command and return the exite code and the output
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            j.logger.info(f"terraform providers mirror succeeded. path: {target_dir}")
        else:
            j.logger.error(f"terraform providers mirror failed. path: {target_dir}")
        return proc.returncode, proc.stdout.decode()

    def init(self, upgrade=False, use_plugin_dir=False):
        """initialize a working directory containing Terraform configuration files. \
            if succeeded, the instance status will be set to INITIALIZED.
        more info: https://www.terraform.io/cli/commands/init

        Args:
            upgrade (bool, optional): Opt to upgrade modules and plugins as part of their respective installation steps. Defaults to False.
            use_plugin_dir (bool, optional): Force plugin installation to read plugins only from {PLUGIN_DIR} \
                this optionally making plugins available locally to avoid repeated re-installation. Defaults to False.

        Returns:
            int: command exit code
        """
        cmd = ["init"]
        if upgrade:
            cmd.append(_INIT_ARGS["upgrade"])
        if use_plugin_dir:
            cmd.append(_INIT_ARGS["plugin-dir"])
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
        return proc.returncode

    def apply(self, vars=None):
        """create a new execution plan then apply the changes in the plan.

        Args:
            vars (dict, optional): dict of the values for input variables declared in your root module. Defaults to None.

        Returns:
            tuple(int, list[dict]):
                exit code of the command
                list of dicts represents the command output as Machine-Readable UI messages. \
                    see: https://www.terraform.io/internals/machine-readable-ui
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
        return proc.returncode, list(map(json.loads, proc.stdout.decode().splitlines()))

    def destroy(self, vars=None):
        """Destroy the terraform managed infrastructure.

        Args:
            vars (dict, optional): dict of the values for input variables declared in your root module. Defaults to None.

        Returns:
            tuple(int, list[dict]):
                exit code of the command
                list of dicts represents the command output as Machine-Readable UI messages. \
                    see: https://www.terraform.io/internals/machine-readable-ui
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
        messages = list(map(json.loads, proc.stdout.decode().splitlines()))
        return proc.returncode, messages

    def get_state_list(self, filter_by_resource=None, filter_by_id=None):
        """list resources within a Terraform state. If no filter/address are given, all resources are listed.

        Args:
            filter_by_resource ([type], optional): [description]. Defaults to None.
            filter_by_id ([type], optional): [description]. Defaults to None.

        Returns:
            tuple(int, list[string]):
                exit code of the command
                list of the resources
        """
        cmd = ["state", "list"]
        if filter_by_id:
            cmd.append(f"-id={filter_by_id}")
        elif filter_by_resource:
            cmd.append(f"{filter_by_resource}")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return proc.returncode, proc.stdout.decode().splitlines()

    def get_output(self, output_name=None):
        """return the output values exported by a terraform module.

        Args:
            output_name (string, optional): the name of a specific output. Defaults to None.

        Returns:
            tuple(int, string or list[string]):
                exit code of the command
                string if a specific output is requested, otherwise dict contain all the output values.
        """
        cmd = ["output"]
        cmd.extend(_OUTPUT_ARGS.values())
        if output_name:
            cmd.append(f"{output_name}")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            return proc.returncode, json.loads(proc.stdout.decode())

        return proc.returncode, proc.stdout.decode()

    def validate_hcl(self):
        """Validate the .tf files in the state dir of the instance.
            see: https://www.terraform.io/docs/commands/validate
       
        Returns:
            tuple(int, dict):
                exit code of the command
                dict of the validation results \

        Example:
            >>> tf.validate_hcl()
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
        except json.decoder.JSONDecodeError:
            output = proc.stdout.decode()
        return proc.returncode, output

    def show(self):
        """Show the terraform managed infrastructure state.

        Returns:
            tuple(int, dict):
                exit code of the command
                dict represents the current state.
        """
        cmd = ["show"]
        cmd.extend(_OUTPUT_ARGS.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        try:
            output = json.loads(proc.stdout.decode())
        except json.decoder.JSONDecodeError:
            output = proc.stdout.decode()
        return proc.returncode, output

    def plan(self, vars=None):
        """creates an execution plan

        Args:
            vars (dict, optional): dict of the values for input variables declared in your root module. Defaults to None.

        Returns:
            tuple(int, list[dict]):
                exit code of the command. 0 if no changes are required, 1 if there was an error, 2 if changes are required.
                list of dicts represents the command output as Machine-Readable UI messages. \
                    see: https://www.terraform.io/internals/machine-readable-ui
        """
        cmd = ["plan"]
        if vars:
            for key, value in vars.items():
                cmd.append(f"-var={key}={value}")
        cmd.extend(_OUTPUT_ARGS.values())
        cmd.append("-detailed-exitcode")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return proc.returncode, list(map(json.loads, proc.stdout.decode().splitlines()))

    def get_plan_summary(self, vars=None):
        """returns the summary of the plan

        Returns:
            tuple(int, dict):
                exit code of the command
                dict represents the summary of the plan.

        Example:
            >>> tf.get_plan_summary(vars={"user": "test"})
            (0, {'add': 0, 'change': 0, 'remove': 0, 'operation': 'plan'})
        """
        rc, messages = self.plan(vars)
        if rc == 0 or rc == 2:
            return rc, self.parse_messages(messages, type="change_summary", key="changes")[0]
        return rc, {}
    
    # TODO: add wrokspace support
