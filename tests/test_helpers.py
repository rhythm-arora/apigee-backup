from commands.helpers import build_req_url
import unittest


class TestHelpers(unittest.TestCase):
    def test_build_req_url_with_env(self):
        self.assertEqual(
            build_req_url("test-org", "apiproduct", "test"),
            "https://api.enterprise.apigee.com/v1/o/test-org/e/test/apiproduct",
        )

    def test_build_req_url_without_env(self):
        self.assertEqual(
            build_req_url("test-org", "apiproxy"),
            "https://api.enterprise.apigee.com/v1/o/test-org/apiproxy",
        )


if __name__ == "__main__":
    unittest.main()
