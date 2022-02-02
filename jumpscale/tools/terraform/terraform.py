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

## Usage

### Basic usage

```python
tf = j.tools.terraform.get("user_name")
tf.hcl_content = "tf file content"  # optionally specify the tf file content needed to create the infrastructure
instance.extra_env = {'MNEMONICS': 'mnemonics',
                      'NETWROK': 'test'}
tf.init_repo()
tf.plan()
tf.apply()
tf.destroy()
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

class TFStatus(Enum):
    NEW = auto()
    INITIALIZED = auto()
    APPLIED = auto()
    DESTROYED = auto()
    ERROR = auto()

class Terraform(Base):

    extra_env = fields.Typed(dict, default={})
    _hcl_content = fields.String()
    status = fields.Enum(TFStatus)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._check_install(TF_BINARY)
        self._env = None

        self.global_args = {
            "chdir": f"-chdir={self.state_dir}",
            }
        self.autoamte_args = {
            "no-input": "-input=false",
            "no-color": "-no-color",
        }
        self.apply_args = {
            "parallelism": "-parallelism=1",
            "auto-approve": "-auto-approve",
            "json": "-json",
        }
        self.init_args = {
            "plugin-dir": "-plugin-dir={PLUGIN_DIR}",
            "upgrade": "-upgrade",
        }
        self.output_args = {
            "json": "-json",
            "no-color": "-no-color",
        }

    def _check_install(self, binary):
        """Check if the binary is installed.

        Args:
            binary (string): binary name

        Raises:
            NotFound: if binary not installed
        """
        if subprocess.call(["which", binary], stdout=subprocess.DEVNULL):
            raise NotFound(f"{binary} not installed")

    @property
    def state_dir(self):
        """Return the path for the directory containing the .tf files for this instance.

        Returns:
            string: dir path
        """
        return os.path.join(STATES_DIR, self.instance_name)

    @property
    def env(self):
        """update the environment variables with ones provided in extra_extra_env to run terraform.

        Returns:
            [type]: [description]
        """
        self.validate()
        self._env = os.environ.copy()
        self._env.update(**self.extra_env)
        return self._env

    @property
    def hcl_content(self):
        """Return the content of the .tf file for this instance.

        Returns:
            [type]: [description]
        """
        # try to open main.tf in state dir if exists
        # filename = os.path.join(self.state_dir, "main.tf")
        # if os.path.exists(filename):
        #     with open(filename, "r") as f:
        #        self._hcl_content = f.read()
        return self._hcl_content
    
    @hcl_content.setter
    def hcl_content(self, value):
        """Create the state dir if it does not exist then write the content to main.tf.
        note: it will overwrite the main.tf file if it exists.
        this could potentially cause issues if the user has apply the infrastructure.

        Args:
            value ([type]): [description]

        Returns:
            [type]: [description]
        """
        os.makedirs(self.state_dir, exist_ok=True)
        flag = "w" # if overwrite else "x"
        filename = f"{self.state_dir}/main.tf"
        with open(filename, flag) as f:
            f.write(value)

        j.logger.debug(f"hcl content saved to: {filename}")
        self._hcl_content = value

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
        full_cmd = [TF_BINARY, *self.global_args.values(), *cmd]
        j.logger.debug(f"Running command: {full_cmd}")
        proc = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.env)
        if check and proc.returncode:
            raise Runtime(f"terraform command failed with {proc.stdout.decode()}/n {proc.stderr.decode()}")
        return proc

    def _construct_args(self, args):
        """Construct the arguments for a terraform command.

        Args:
            args (list[string]): multiple args keys to extract the values from self.args

        Returns:
            list[string]: multiple values for the args keys
        """
        # TODO: to refactor and use this
        return [v for (k, v) in self.autoamte_args.items() if k in args]

    def _log_proc_output(self, proc):
        """Log the output of a subprocess.

        Args:
            proc (subprocess.Popen): object containe the output of the command and the exit code.
        """
        j.logger.debug(f"STDOUT:\n{proc.stdout.decode()}")
        if proc.stderr:
            j.logger.debug(f"STDERR:\n{proc.stderr.decode()}")
        j.logger.debug(f"EXIT CODE: {proc.returncode}")


    def init_dir(self, upgrade = False, use_plugin_dir=False):
        """Init terraform dir.

        Args:
            upgrade (bool, optional): [description]. Defaults to False.
            use_plugin_dir (bool, optional): [description]. Defaults to False.

        Returns:
            int: command exit code
        """
        cmd = ["init"]
        if upgrade:
            cmd.append(self.init_args["upgrade"])
        if use_plugin_dir:
            cmd.append(self.init_args["plugin-dir"])
        cmd.extend(self.autoamte_args.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            self.status = TFStatus.INITIALIZED
            self.save()
        return proc.returncode

    def apply(self, vars=None):
        """Apply the terraform managed infrastructure.

        Args:
            vars ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        cmd = ["apply"]
        if vars:
            # apply -var for every key value pair
            for key, value in vars.items():
                cmd.append(f"-var={key}={value}")
        cmd.extend(self.autoamte_args.values())
        cmd.extend(self.apply_args.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            self.status = TFStatus.APPLIED
        else:
            self.status = TFStatus.ERROR
        self.save()
        return proc.returncode, list(map(json.loads, proc.stdout.decode().splitlines()))

    def destroy(self, vars=None):
        """Destroy the terraform managed infrastructure.

        Args:
            vars ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        cmd = ["destroy"]
        if vars:
            # apply -var for every key value pair
            for key, value in vars.items():
                cmd.append(f"-var={key}={value}")
        cmd.extend(self.autoamte_args.values())
        cmd.extend(self.apply_args.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        if proc.returncode == 0:
            self.status = TFStatus.DESTROYED
        else:
            self.status = TFStatus.ERROR
        self.save()
        return proc.returncode, list(map(json.loads, proc.stdout.decode().splitlines()))

    def get_state_list(self, filter_by_resource=None, filter_by_id=None):
        """[summary]

        Args:
            filter_by_resource ([type], optional): [description]. Defaults to None.
            filter_by_id ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        cmd = ["state", "list"]
        if filter_by_id:
            cmd.append(f"-id={filter_by_id}")
        elif filter_by_resource:
            cmd.append(f"{filter_by_resource}")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return proc.returncode, proc.stdout.decode().splitlines()
    
    def get_terraform_output(self, output_name=None):
        """[summary]

        Args:
            output_name ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        cmd = ["output"]
        cmd.extend(self.output_args.values())
        if output_name:
            cmd.append(f"{output_name}")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return proc.returncode, json.loads(proc.stdout.decode())

    def validate_hcl(self):
        """Validate the terraform managed infrastructure.

        Returns:
            [type]: [description]
        """
        cmd = ["validate"]
        cmd.extend(self.output_args.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return proc.returncode, json.loads(proc.stdout.decode())

    def show(self):
        """Show the terraform managed infrastructure state.

        Returns:
            [type]: [description]
        """
        cmd = ["show"]
        cmd.extend(self.output_args.values())
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return proc.returncode, json.loads(proc.stdout.decode())
    
    def plan(self, vars=None):
        """Plan the terraform managed infrastructure.

        Args:
            vars ([type], optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        cmd = ["plan"]
        for key, value in vars.items():
            cmd.append(f"-var={key}={value}")
        cmd.extend(self.output_args.values())
        cmd.append("-detailed-exitcode")
        proc = self._run_cmd(cmd)
        self._log_proc_output(proc)
        return proc.returncode, list(map(json.loads, proc.stdout.decode().splitlines()))
    
    def prase_messages(self, messages, type, key=None):
        """Parse terraform messages to get a specific messages/message or values/value.

        Args:
            messages ([type]): [description]
            type ([type]): [description]
            key ([type], optional): [description]. Defaults to None.
            latest (bool, optional): [description]. Defaults to False.

        Returns:
            [type]: [description]
        
        Examples:
            >>> tf = j.tools.terraform.get("samehabouelsaad")
            >>> rc, messages = tf.plan(vars={"user": "abouelsaad"})
            >>> tf.prase_messages(messages, type="change_summary", key="changes")
            [{'add': 0, 'change': 0, 'remove': 0, 'operation': 'plan'}]
        """
        messages_with_type = [message for message in messages if message["type"] == type] # filter messages by type
        if key:
            values = [message[key] for message in messages_with_type if message.get(key)]
            return values
        return messages_with_type
