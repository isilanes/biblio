from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User


class TestViews(TestCase):

    USERNAME = "random_user"
    PASSWORD = "random_password"
    SLUGS_THAT_NEED_LOGIN = {
        "stats",
        "index",
        "sagas",
    }

    def setUp(self):
        self._create_user()

    def tearDown(self):
        pass

    def _create_user(self):
        User.objects.create_user(username=self.USERNAME, password=self.PASSWORD).save()

    def test_that_GETs_redirect_to_login(self):
        for slug in self.SLUGS_THAT_NEED_LOGIN:
            url = reverse(f"books:{slug}")
            response = self.client.get(url)
            self.assertRedirects(response,
                                 f"/login?next={url}",
                                 status_code=302,
                                 target_status_code=301,
                                 fetch_redirect_response=True)

    def test_we_can_log_in(self):
        log_in = self.client.login(username=self.USERNAME, password=self.PASSWORD)
        self.assertTrue(log_in)

    def tests_GETs_when_logged(self):
        self.client.login(username=self.USERNAME, password=self.PASSWORD)
        for slug in self.SLUGS_THAT_NEED_LOGIN:
            url = reverse(f"books:{slug}")
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
