import pytest
from jumpscale.loader import j
from unittest import TestCase
import tempfile
from pathlib import Path
import string
from jumpscale.tools.terraform.terraform import TFStatus

CONTENT = """
variable "input_var" {
  type = string
  default = "default"
}


resource "null_resource" "null_resource" {
    provisioner "local-exec" {
        command = "echo ${var.input_var}"
    }
}

output "output_var" {
  value = "${var.input_var}"
}
"""

class Test_Terrform_Happy_Flow(TestCase):
    @staticmethod
    def random_name():
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)
    
    @classmethod
    def setUpClass(cls):
        # root dir will have all test created files
        cls.ROOT_DIR = Path(tempfile.mkdtemp())
        # example configuration module with a null resource + random provider
        cls.TF_SOURCE_MODULE_DIR = cls.ROOT_DIR / "tf_source_module"
        cls.TF_SOURCE_MODULE_DIR.mkdir()
        cls.f = cls.TF_SOURCE_MODULE_DIR / "main.tf"
        cls.f.write_text(CONTENT)

        j.logger.info("ROOT_DIR: {cls.ROOT_DIR}")
        cls.PLUGIN_DIR = cls.ROOT_DIR / "tf_plugins"
        cls.PLUGIN_DIR.mkdir()
        cls.STATES_DIR = cls.ROOT_DIR / "tf_states"
        cls.STATES_DIR.mkdir()
        cls.CACHE_DIR = cls.ROOT_DIR / "tf_cache"
        cls.CACHE_DIR.mkdir()

    def setUp(self):
        super().setUp()
        self.instance_name = self.random_name()
        self.state_dir = j.sals.fs.join_paths(self.STATES_DIR, self.instance_name)
        self.tf = j.tools.terraform.get(self.instance_name)
        self.tf.source_module = str(self.TF_SOURCE_MODULE_DIR)
        self.tf.plugin_dir = str(self.PLUGIN_DIR)
        self.tf.state_dir = str(self.state_dir)

        self.tf.extra_env.update({"TF_PLUGIN_CACHE_DIR": str(self.CACHE_DIR)})
        self.tf.save()  
        j.logger.info(f"test instance:\n{self.tf}")

    def test_01_init_empty_dir_from_source_module(self):
        res = self.tf.init(from_module=True)
        self.assertTrue(j.sals.fs.exists(j.sals.fs.join_paths(self.state_dir, "main.tf")))
        self.assertTrue(res.is_ok)
        
    
    def test_02_copy_source_module(self):
        self.tf.copy_source_module()
        self.assertTrue(j.sals.fs.exists(j.sals.fs.join_paths(self.state_dir, "main.tf")))
    
    def test_03_validate_hcl_valid(self):
        self.tf.init(from_module=True)
        res = self.tf.validate_hcl()
        self.assertTrue(res.is_ok)
        self.assertTrue(res.json["valid"])

    def test_04_init_dir_with_configuration_files(self):
        self.tf.copy_source_module()
        res = self.tf.init()
        self.assertTrue(res.is_ok)
    
    def test_05_plan(self):
        self.tf.init(from_module=True)
        res = self.tf.plan()
        self.assertTrue(res.is_ok)
        self.assertTrue(res.changes_present)
        self.assertTrue(res.plan_summary.get("add") == 1)
    
    def test_06_apply(self):
        self.tf.init(from_module=True)
        res = self.tf.apply()
        self.assertTrue(res.is_ok)
        self.assertTrue(res.apply_summary.get("add") == 1)

    
    def test_07_apply_with_input_vars(self):
        self.tf.init(from_module=True)
        res = self.tf.apply({"input_var": "test_input"})
        self.assertTrue(res.is_ok)

    def test_08_state_list(self):
        self.tf.init(from_module=True)
        res = self.tf.apply()
        self.assertTrue(res.is_ok)
        res = self.tf.get_state_list()
        self.assertTrue(res.is_ok)
        self.assertTrue(len(res.resources) == 1)

    def test_08_output(self):
        self.tf.init(from_module=True)
        res = self.tf.apply({"input_var": "test_input"})
        self.assertTrue(res.is_ok)
        self.assertTrue(res.outputs.get("output_var"))
        self.assertTrue(res.outputs.get("output_var") == "test_input")


    def test_09_show(self):
        self.tf.init(from_module=True)
        res = self.tf.apply()
        self.assertTrue(res.is_ok)
        res = self.tf.show()
        self.assertTrue(res.is_ok)

    def test_10_destroy(self):
        self.tf.init(from_module=True)
        res = self.tf.apply()
        self.assertTrue(res.is_ok)
        res = self.tf.destroy()
        self.assertTrue(res.is_ok)
        self.assertTrue(res.destroy_summary.get("remove") == 1)
        res = self.tf.get_state_list()
        self.assertTrue(res.is_ok)
        self.assertTrue(len(res.resources) == 0)
    
    def test_11_destroy_with_input_vars(self):
        self.tf.init(from_module=True)
        self.tf.apply({"input_var": "test_input"})
        res = self.tf.destroy({"input_var": "test_input"})
        self.assertTrue(res.is_ok)
        
    
    def test_12_tf_status_created(self):
        self.tf.init(from_module=True)
        self.assertTrue(self.tf.status == TFStatus.CREATED)
    
    def test_13_tf_status_applied(self):
        self.tf.init(from_module=True)
        self.tf.apply()
        self.assertTrue(self.tf.status == TFStatus.APPLIED)
    
    def test_14_tf_status_destroyed(self):
        self.tf.init(from_module=True)
        self.tf.apply()
        self.tf.destroy()
        self.assertTrue(self.tf.status == TFStatus.DESTROYED)


    def tearDown(self):
        super().tearDown()
        j.logger.info(f"deleting the instance state dir: {self.state_dir}")
        self.tf._clean_state_dir(force=True)
        j.logger.info(f"deleting tf test instance: {self.instance_name}")
        j.tools.terraform.delete(self.instance_name)

    @classmethod
    def tearDownClass(cls):
        j.logger.info(f"cleaning up {cls.ROOT_DIR}")
        j.sals.fs.rmtree(path=cls.ROOT_DIR)
