from os import path
import pathlib
import unittest

from ninja_bear import Orchestrator, DistributorCredentials
from src.<module-folder>.distributor import Distributor


class Test(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self._test_path = pathlib.Path(__file__).parent.resolve()
        self._test_config_path = path.join(self._test_path, '..', 'example/test-config.yaml')

    def test_distribution(self):
        # Get secret from environment variables.
        credential = DistributorCredentials('example-alias', None, 'password')
        orchestrator = Orchestrator.read_config(self._test_config_path, [credential], plugins=self._plugins)

        orchestrator.distribute()

        # TODO: Add distributor result check here (e.g. if file has been distributed to Git or whatever
        # your distributor does).
        raise Exception('Distributor result checking has not been implemented')
