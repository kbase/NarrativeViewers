import unittest
import os
import os.path
import json
import time
import codecs

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint

from NarrativeMethodStore.NarrativeMethodStoreClient import NarrativeMethodStore


class NarrativeViewersTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('NarrativeViewers'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.nmsURL = cls.cfg['kbase-endpoint'] + "/narrative_method_store/rpc"
        cls.nmsClient = NarrativeMethodStore(cls.nmsURL, token=token)

    @classmethod
    def tearDownClass(cls):
        pass

    def getNmsClient(self):
        return self.__class__.nmsClient

    def test_method_specs(self):
        root_dir = os.path.join("/kb/module", "ui", "narrative", "methods")
        all_ok = True
        for method_id in os.listdir(root_dir):
            print("Method [" + method_id + "]")
            method_dir = os.path.join(root_dir, method_id)
            spec_json = None
            with codecs.open(os.path.join(method_dir, "spec.json"), 'r', "utf-8", errors='ignore') as spec_file:
                spec_json = spec_file.read()
            display_yaml = None
            with codecs.open(os.path.join(method_dir, "display.yaml"), 'r', "utf-8", errors='ignore') as display_file:
                display_yaml = display_file.read()
            extra_files = {}
            ret = self.getNmsClient().validate_method(
                {"id": method_id, "spec_json": spec_json,
                "display_yaml": display_yaml, "extra_files": extra_files})
            is_valid = ret['is_valid']
            if (is_valid == 1):
                print("\tOK")
            else:
                all_ok = False
                print("\tNot valid:")
                errors = ret['errors']
                for error in errors:
                    print("\tError: " + error)
                warns = ret['warnings']
                for warn in warns:
                    print("\tWarning: " + warn)
        self.assertTrue(all_ok)

