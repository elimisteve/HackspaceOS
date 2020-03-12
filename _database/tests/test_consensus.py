from django.test import TestCase
from _database.models import Consensus


class ConsensusTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Consensus.objects.import_from_discourse()

    def test_LIST__search_results(self):
        self.assertTrue(type(Consensus.objects.LIST__search_results()) == list)
