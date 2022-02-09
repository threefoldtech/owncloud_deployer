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
INVALID_CONTENT = """
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
        # example configuration module with a null resource
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
        res = self.tf.apply({"input_var": "test"})
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
        res = self.tf.apply({"input_var": "test"})
        self.assertTrue(res.is_ok)
        self.assertTrue(res.outputs.get("output_var"))
        self.assertTrue(res.outputs.get("output_var") == "test")


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
        self.tf.apply({"input_var": "test"})
        res = self.tf.destroy({"input_var": "test"})
        self.assertTrue(res.is_ok)
        
    
    def test_12_tf_status_created(self):
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

class Test_Terrform_Sad_Flow(TestCase):
    @staticmethod
    def random_name():
        return j.data.idgenerator.nfromchoices(10, string.ascii_lowercase)
    
    @classmethod
    def setUpClass(cls):
        # root dir will have all test created files
        cls.ROOT_DIR = Path(tempfile.mkdtemp())
        # example configuration module with a null resource
        cls.TF_SOURCE_MODULE_DIR = cls.ROOT_DIR / "tf_source_module"
        cls.TF_SOURCE_MODULE_DIR.mkdir()
        cls.f = cls.TF_SOURCE_MODULE_DIR / "main.tf"
        cls.f.write_text(CONTENT)
        # invalid configuration module
        cls.TF_SOURCE_MODULE_DIR_INVALID = cls.ROOT_DIR / "tf_source_module_invalid"
        cls.TF_SOURCE_MODULE_DIR_INVALID.mkdir()
        cls.f = cls.TF_SOURCE_MODULE_DIR_INVALID / "main.tf"
        cls.f.write_text(INVALID_CONTENT)

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

    def test_01_init_empty_dir(self):
        res = self.tf.init()
        self.assertFalse(res.is_ok)
        self.assertTrue(res.last_error)
        self.assertTrue("no such file or directory" in res.last_error)
    
    
    def test_02_copy_source_module_not_set(self):
        self.tf.source_module = None
        # expect pytest to fail
        self.assertRaises(ValueError, self.tf.copy_source_module)
    
    def test_03_copy_source_module_not_exists(self):
        self.tf.source_module = "/tmp/not_exists"
        # expect pytest to fail
        self.assertRaises(FileNotFoundError, self.tf.copy_source_module)
    
    def test_04_validate_hcl_invalid(self):
        self.tf.source_module = str(self.TF_SOURCE_MODULE_DIR_INVALID)
        self.tf.save()
        self.tf.init(from_module=True)
        res = self.tf.validate_hcl()
        self.assertFalse(res.is_ok)
        self.assertFalse(res.json["valid"])
        self.assertTrue(res.json.get("error_count"))
        self.assertTrue(res.json.get("diagnostics"))

    
    def test_05_plan_invalid(self):
        self.tf.source_module = str(self.TF_SOURCE_MODULE_DIR_INVALID)
        self.tf.save()
        self.tf.init(from_module=True)
        res = self.tf.plan()
        self.assertFalse(res.is_ok)
        self.assertTrue(res.errors)
        self.assertTrue(res.last_error)

    
    def test_06_apply_fail(self):
        self.tf.init(from_module=True)
        res = self.tf.apply({"input_not_exists": "test_input"})
        self.assertTrue(res.errors)
        self.assertTrue(res.last_error)


    def test_07_state_list_no_applied_configuration(self):
        self.tf.init(from_module=True)
        res = self.tf.get_state_list()
        self.assertFalse(res.is_ok)
        self.assertTrue("No state file was found!" in res.last_error)   


    def test_08_destroy_no_applied_configuration(self):
        self.tf.init(from_module=True)
        # res = self.tf.apply()
        # self.assertTrue(res.is_ok)
        res = self.tf.destroy()
        self.assertTrue(res.is_ok)
        self.assertTrue(res.destroy_summary.get("remove") == 0)
        res = self.tf.get_state_list()
        self.assertTrue(res.is_ok)
        self.assertTrue(len(res.resources) == 0)
    
    def test_09_destroy_fail(self):
        # TODO
        pass

    def test_10_tf_status_applied_fail(self):
        self.tf.init(from_module=True)
        res = self.tf.apply({"input_not_exists": "test_input"})
        self.assertFalse(res.is_ok)
        self.assertTrue(self.tf.status == TFStatus.FAILED_TO_APPLY)
    
    def test_11_tf_status_destroyed_fail(self):
        # TODO
        pass


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