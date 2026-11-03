import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from intelligence.evidence import build_evidence_ledger


class EvidenceLedgerTests(unittest.TestCase):
    def test_records_independent_support_without_claiming_full_agreement(self):
        article = {
            'title': 'Poland coalition faces election turmoil',
            'source': 'Reuters',
            'link': 'https://example.test/reuters',
            'storyCluster': {'sources': [
                {'source': 'Reuters', 'title': 'Poland coalition faces election turmoil'},
                {'source': 'AP News', 'title': 'Poland coalition confronts election turmoil'},
            ]},
        }
        claim = build_evidence_ledger(article)['claims'][0]
        self.assertEqual(claim['classification'], 'directly_reported')
        self.assertEqual(claim['evidence'][0]['quote'], article['title'])
        self.assertEqual(claim['corroboration']['independent_sources'][0]['source'], 'AP News')
        self.assertIn('not agreement', claim['corroboration']['method'])

    def test_flags_numeric_conflict_for_review(self):
        article = {
            'title': 'Flood kills 10 people in region',
            'source': 'Reuters',
            'storyCluster': {'sources': [
                {'source': 'Reuters', 'title': 'Flood kills 10 people in region'},
                {'source': 'BBC', 'title': 'Flood kills 12 people in region'},
            ]},
        }
        ledger = build_evidence_ledger(article)
        claim = ledger['claims'][0]
        self.assertTrue(ledger['review_required'])
        self.assertTrue(claim['disputed']['present'])
        self.assertEqual(claim['disputed']['signals'][0]['signal'], 'different numeric detail')

    def test_single_source_stays_limited(self):
        ledger = build_evidence_ledger({'title': 'Single source report', 'source': 'Reuters'})
        claim = ledger['claims'][0]
        self.assertTrue(ledger['review_required'])
        self.assertEqual(claim['confidence']['label'], 'moderate')
        self.assertIn('headlines alone', claim['unknown'][0])


if __name__ == '__main__':
    unittest.main()
