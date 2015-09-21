from datetime import datetime
import unittest
from elife_hw_metrics import core

class BaseCase(unittest.TestCase):
    maxDiff = None

class TestUtils(BaseCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_metrics_between(self):

        start_date = datetime(year=2014, month=1, day=1),
        end_date = datetime(year=2014, month=1, day=1)
        results = core.metrics_between(start_date, end_date, 'daily') # same day
        expected_results = [] # we have no daily metrics for this time range
        self.assertEqual(results, expected_results)
