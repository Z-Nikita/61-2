from django.test import TestCase


class MoviesSmokeTest(TestCase):
    def test_movies_page_opens(self):
        response = self.client.get("/movies/")
        self.assertEqual(response.status_code, 200)
