import unittest
from pathlib import Path

class ComplianceTests(unittest.TestCase):
    def test_approved_skill_copy_exists_and_retired_skill_absent(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / 'skills/consumer-insight/SKILL.md').exists())
        self.assertFalse((root / 'skills/retired-business-skill-directory').exists())

if __name__ == '__main__':
    unittest.main()


