from datetime import datetime
import unittest
from elife_hw_metrics import core
from collections import OrderedDict

class BaseCase(unittest.TestCase):
    maxDiff = None

class TestUtils(BaseCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_intorbust(self):
        cases = {
            # given -> expected
            "1": 1,
            "-1": -1,
            "1.1": 1,
            "1.9999": 1,
            "a": "a",
            (1, 1): (1, 1),
            None: None
        }
        for given, expected in cases.items():
            self.assertEqual(core.intorbust(given), expected)

    def test_exsubdict(self):
        data = {'a': 1, 'b': 2, 'c': 3}
        cases = [
            # given -> expected
            (['a'], ['b', 'c']),
            (['a', 'b'], ['c']),
            (['a', 'b', 'c'], []),
        ]
        for args, expected in cases:
            res = core.exsubdict(data, args)
            self.assertEqual(len(res), len(expected))
            self.assertTrue(all([expected_key in res for expected_key in expected]))
            for key in res.keys():
                self.assertEqual(data[key], res[key])
            
    def test_dictmap(self):
        data = {'a': 1, 'b': 2, 'c': 3}
        inc = lambda v: v+1
        dec = lambda v: v-1
        cases = [
            # given -> expected
            (inc, {'a': 2, 'b': 3, 'c': 4}),
            (dec, {'a': 0, 'b': 1, 'c': 2}),
            (str, {'a': '1', 'b': '2', 'c': '3'}),
        ]
        for func, expected in cases:
            self.assertEqual(core.dictmap(func, data), expected)

    def test_format_date(self):
        cases = [
            # given -> expected
            ('200101', '2001-01'),
            ('20010101', '2001-01-01'),
            # bad dates but we don't deal with correctness here
            ('99999999', '9999-99-99'),
            ('abcdefgh', 'abcd-ef-gh'),
        ]
        for arg, expected in cases:
            self.assertEqual(core.format_date(arg), expected)

    def test_format_date_failures(self):
        cases = [
            '',
            '12345',
            '1234567',
            '123456789',
        ]
        for arg in cases:
            self.assertRaises(ValueError, core.format_date, arg)

    def test_in_range(self):
        pass

    def test_fname_to_dt(self):
        pass

    def test_metrics_between(self):
        start_date = datetime(year=2014, month=1, day=1)
        end_date = datetime(year=2014, month=1, day=1)
        results = core.metrics_between(start_date, end_date, 'daily') # same day
        expected_results = OrderedDict([]) # we have no daily metrics for this time range
        self.assertEqual(results, expected_results)
