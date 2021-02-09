import unittest
from case_parsers import seq_match


class TestCaseParsers(unittest.TestCase):
    def test_check_seq_match_model(self):
        ok = seq_match.check_seq_match_model()
        self.assertTrue(ok)

    def test_seq_match(self):
        ratio = seq_match.seq_match(
            '由被告承担本案的诉讼费用',
            '被告董立华未发表答辩意见。')
        print(ratio)
        self.assertTrue(ratio > 0 and ratio < 1)


if __name__ == '__main__':
    unittest.main()
