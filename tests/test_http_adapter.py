import unittest

from adapters.http_endpoint import validate_url


class HttpAdapterSafetyTests(unittest.TestCase):
    def test_https_remote_allowed(self):
        self.assertEqual(
            validate_url("https://agent.example.com/sao"),
            "https://agent.example.com/sao",
        )

    def test_remote_plain_http_rejected(self):
        with self.assertRaises(ValueError):
            validate_url("http://agent.example.com/sao")

    def test_localhost_http_allowed_for_local_experiment(self):
        self.assertEqual(
            validate_url("http://127.0.0.1:8123/sao"),
            "http://127.0.0.1:8123/sao",
        )

    def test_credentials_in_url_rejected(self):
        with self.assertRaises(ValueError):
            validate_url("https://user:secret@agent.example.com/sao")

    def test_relative_url_rejected(self):
        with self.assertRaises(ValueError):
            validate_url("/sao")


if __name__ == "__main__":
    unittest.main()
