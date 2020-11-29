import unittest
import test
from case_parsers import case_info


class TestCaseParsers(unittest.TestCase):
    def test_get_cause(self):
        cause = case_info.get_cause(test.lines)
        self.assertEqual(cause, '机动车交通事故责任纠纷')

    def test_get_case_type(self):
        case_type = case_info.get_case_type(test.lines)
        self.assertEqual(case_type, '民事一审案件')


if __name__ == '__main__':
    unittest.main()
