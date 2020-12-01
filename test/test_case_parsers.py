import unittest
import test
from case_parsers import case_info


class TestCaseParsers(unittest.TestCase):
    def test_get_cause(self):
        cause = case_info.get_cause(test.lines)
        self.assertEqual(cause, test.fields["cause"])

    def test_get_case_type(self):
        case_type = case_info.get_case_type(test.lines)
        self.assertEqual(case_type, test.fields["case_type"])

    def test_get_court(self):
        court = case_info.get_court(test.lines)
        self.assertEqual(court, test.fields["court"])


if __name__ == '__main__':
    unittest.main()
