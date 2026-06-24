from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from apps.resources.models import Prison

class PrisonModelTest(TestCase):
    def test_auto_code_generation(self):
        # Create a prison with no code
        prison = Prison.objects.create(
            name="Test Halfway House",
            type="HALFWAY_HOUSE",
            city="Atlanta",
            state="GA"
        )
        self.assertTrue(prison.code.startswith("LOC-"))
        self.assertEqual(len(prison.code), 12) # LOC- (4) + 8 hex chars = 12

    def test_custom_code_preserved(self):
        # Create a prison with an explicit code
        prison = Prison.objects.create(
            code="MYCODE123",
            name="Test Prison",
            type="FCI",
            city="New York",
            state="NY"
        )
        self.assertEqual(prison.code, "MYCODE123")

class PrisonAPITestCase(APITestCase):
    def setUp(self):
        # Create different types of locations
        self.prison1 = Prison.objects.create(
            code="PR1",
            name="Federal Prison Camp Alderson",
            type="FPC",
            city="Alderson",
            state="WV",
            latitude=37.7244,
            longitude=-80.6424
        )
        self.prison2 = Prison.objects.create(
            code="PR2",
            name="FCI Aliceville",
            type="FCI",
            city="Aliceville",
            state="AL",
            latitude=33.1294,
            longitude=-88.1614
        )
        self.halfway_house1 = Prison.objects.create(
            code="HH1",
            name="Atlanta RRM",
            type="RRM",
            city="Atlanta",
            state="GA",
            latitude=33.7490,
            longitude=-84.3880
        )
        self.halfway_house2 = Prison.objects.create(
            code="HH2",
            name="Custom Halfway House",
            type="HALFWAY_HOUSE",
            city="Miami",
            state="FL",
            latitude=25.7617,
            longitude=-80.1918
        )

    def test_prison_list_no_filter(self):
        response = self.client.get('/api/v1/prisons/')
        # By default it returns all sorted by id
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify result contains all items (pagination is enabled so check results count or results array)
        self.assertEqual(response.data['count'], 4)

    def test_prison_list_filter_prison(self):
        response = self.client.get('/api/v1/prisons/', {'category': 'prison'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Excludes only HALFWAY_HOUSE (should be 3 items: PR1, PR2, HH1)
        self.assertEqual(response.data['count'], 3)
        codes = [item['code'] for item in response.data['results']]
        self.assertIn("PR1", codes)
        self.assertIn("PR2", codes)
        self.assertIn("HH1", codes)
        self.assertNotIn("HH2", codes)

    def test_prison_list_filter_halfway_house(self):
        response = self.client.get('/api/v1/prisons/', {'category': 'halfway_house'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only HALFWAY_HOUSE (should be 1 item: HH2)
        self.assertEqual(response.data['count'], 1)
        codes = [item['code'] for item in response.data['results']]
        self.assertNotIn("HH1", codes)
        self.assertIn("HH2", codes)
        self.assertNotIn("PR1", codes)
        self.assertNotIn("PR2", codes)

    def test_locations_list_filter_prison(self):
        response = self.client.get('/api/v1/locations/', {'category': 'prison'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        names = [item['name'] for item in response.data]
        self.assertIn(self.prison1.name, names)
        self.assertIn(self.halfway_house1.name, names)

    def test_locations_list_filter_halfway_house(self):
        response = self.client.get('/api/v1/locations/', {'category': 'halfway_house'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        names = [item['name'] for item in response.data]
        self.assertNotIn(self.halfway_house1.name, names)
        self.assertIn(self.halfway_house2.name, names)
        self.assertNotIn(self.prison1.name, names)
