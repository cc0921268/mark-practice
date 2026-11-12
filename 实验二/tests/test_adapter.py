import io
import unittest
from pathlib import Path
from src.consumer_insight_adapter import AdapterError, analyze_reviews_csv, analyze_reviews_file

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.csv = Path('data/sample/reviews.csv').read_bytes()
    def test_sample_contract_and_evidence(self):
        result = analyze_reviews_csv(self.csv)
        self.assertEqual(len(result['records']), 10)
        self.assertEqual(result['records'][0]['sentiment'], 'positive')
        for row in result['records']:
            for value in row['evidence'].values():
                for quote in value if isinstance(value, list) else [value]:
                    if quote: self.assertIn(quote, row['review'])
    def test_missing_and_duplicate_rejected(self):
        with self.assertRaises(AdapterError): analyze_reviews_csv(b'review_id\nR1\n')
        with self.assertRaises(AdapterError): analyze_reviews_csv(b'review_id,review\nR1,x\nR1,y\n')
    def test_empty_review_unknown(self):
        row = analyze_reviews_csv(b'review_id,review\nR1,\n')['records'][0]
        self.assertEqual(row['sentiment'], 'unknown')
        self.assertEqual(row['confidence'], 0.0)
    def test_path_boundary(self):
        with self.assertRaises(AdapterError): analyze_reviews_file(Path('..') / 'outside.csv')

if __name__ == '__main__': unittest.main()
