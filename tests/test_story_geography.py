import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS = os.path.join(_ROOT, 'scripts')
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from intelligence.geography import enrich_story_geography


class StoryGeographyTests(unittest.TestCase):
    def test_event_geography_overrides_publisher_section(self):
        article = {
            'region': 'North America',
            'entities': {'countries': [{'code': 'PL', 'name': 'Poland'}, {'code': 'RU', 'name': 'Russia'}]},
            'primary_actors': {'active_agent': 'Russia Sovereign Authorities', 'leaders': [], 'sovereign_stakeholders': ['Russia', 'Poland']},
        }

        enrich_story_geography(article)

        self.assertEqual(article['source_region'], 'North America')
        self.assertEqual(article['region'], 'Europe')
        self.assertEqual(article['geography']['event_regions'], ['Europe'])
        self.assertEqual(article['geography']['strategic_theatre'], 'European Security')

    def test_unknown_location_keeps_source_context_without_faking_evidence(self):
        article = {'region': 'Global', 'entities': {}, 'primary_actors': {}}

        enrich_story_geography(article)

        self.assertEqual(article['region'], 'Global')
        self.assertEqual(article['geography']['event_regions'], [])
        self.assertEqual(article['geography']['confidence'], 'source-context')


if __name__ == '__main__':
    unittest.main()
