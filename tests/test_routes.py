import unittest
from types import SimpleNamespace
from vcr_unittest import VCRTestCase
from webapp.app import app, set_default_cache_control


class TestRoutes(VCRTestCase):
    def _get_vcr_kwargs(self):
        """
        This removes the authorization header
        from VCR so we don't record auth parameters
        """
        return {
            "decode_compressed_response": True,
            "filter_headers": [
                "Authorization",
                "Cookie",
                "Api-Key",
                "Api-username",
            ],
        }

    def setUp(self):
        """
        Set up Flask app for testing
        """
        app.testing = True
        self.client = app.test_client()
        return super().setUp()

    def test_homepage(self):
        """
        When given the index URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/").status_code, 200)

    def test_iot_page(self):
        """
        When given the iot page URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/iot").status_code, 200)

    def test_iot(self):
        """
        When given the iot URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/iot").status_code, 200)

    def test_ai_ml(self):
        """
        When given the ai-ml URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/ai-ml").status_code, 200)

    def test_kubernetes(self):
        """
        When given the kubernetes URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/kubernetes").status_code, 200)

    def test_pricing(self):
        """
        When given the pricing URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/pricing").status_code, 200)

    def test_contact_us(self):
        """
        When given the contact-us URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/contact-us").status_code, 200)

    def test_thank_you(self):
        """
        When given the thank-you URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/thank-you").status_code, 200)

    def test_robotics_whitepaper(self):
        """
        When given the engage robotics_whitepaper URL,
        we should return a 200 status code
        """

        self.assertEqual(
            self.client.get("/engage/robotics_whitepaper").status_code, 200
        )

    def test_not_found(self):
        """
        When given a non-existent URL,
        we should return a 404 status code
        """

        self.assertEqual(self.client.get("/not-found-url").status_code, 404)

    def test_blog(self):
        """
        When given the blog URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/blog").status_code, 200)

    def test_openstack(self):
        """
        When given the openstack URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/openstack").status_code, 200)

    def test_pro(self):
        """
        When given the pro URL,
        we should return a 200 status code
        """

        self.assertEqual(self.client.get("/pro").status_code, 200)

    def test_default_cache_control_is_one_hour(self):
        """
        Pages should be cacheable by content-cache for 1 hour,
        overriding the 60s default from flask-base
        """

        response = self.client.get("/")
        self.assertEqual(response.cache_control.max_age, 3600)

    def test_explicit_string_cache_control_is_preserved(self):
        """
        Responses with an explicit string max-age should not be overridden
        by the 1 hour default cache-control policy
        """

        with app.test_request_context("/"):
            response = SimpleNamespace(
                status_code=200,
                cache_control=SimpleNamespace(
                    no_store=False,
                    no_cache=False,
                    private=False,
                    max_age="300",
                ),
            )
            response = set_default_cache_control(response)

        self.assertEqual(response.cache_control.max_age, "300")


if __name__ == "__main__":
    unittest.main()
