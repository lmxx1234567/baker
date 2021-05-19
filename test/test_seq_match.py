import unittest
from case_parsers import sequence_match
import test


class TestSeqMatch(unittest.TestCase):
    def test_check_seq_match_model(self):
        ok = sequence_match.check_seq_match_model()
        self.assertTrue(ok)

    def test_seq_match(self):
        for line in test.lines:
            ratio = sequence_match.seq_match(
                '1.依法判令被告赔偿医疗费、死亡赔偿金、丧葬费、误工费、交通费、被扶养人生活费、精神损害赔偿金、财产损失等共计368，748元；',
                line)
            print(ratio)
            if ratio > 0.5:
                print(line)
            self.assertTrue(ratio > 0 and ratio < 1)


if __name__ == '__main__':
    unittest.main()
