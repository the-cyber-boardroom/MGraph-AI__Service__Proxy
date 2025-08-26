from unittest                                    import TestCase
from tests.deploy_aws.test_Deploy__Service__base import test_Deploy__Service__base
from osbot_utils.utils.Dev                       import pprint

class test_Deploy__Service__to__dev(test_Deploy__Service__base, TestCase):
    stage = 'dev'

    # def test__invoke_return_logs(self):
    #     self.deploy_fast_api.create()
    #     response = self.deploy_fast_api.lambda_function().invoke_return_logs({})
    #     pprint(response)