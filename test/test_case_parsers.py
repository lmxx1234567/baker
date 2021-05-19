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

    def test_get_judge(self):
        judge = case_info.get_judge(test.lines)
        self.assertEqual(judge, test.fields["judge"])

    def test_get_clerk(self):
        clerk = case_info.get_clerk(test.lines)
        self.assertEqual(clerk, test.fields["clerk"])

    def test_get_claims(self):
        claims = case_info.get_claims(test.lines)
        print(claims)

    def test_get_controversies(self):
        controversies = case_info.get_controversies(test.lines)
        print(controversies)

    def test_get_case_summary(self):
        case_summary = case_info.get_case_summary(test.lines)
        print(case_summary)


if __name__ == '__main__':
    unittest.main()
