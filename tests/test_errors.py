import unittest
from urllib.error import HTTPError
from src.errors import SafeError,safe_error

class ErrorTests(unittest.TestCase):
    def test_auth_status_without_private_details(self):
        message=safe_error(HTTPError('https://example.com?key=private',401,'private-token',None,None))
        self.assertIn('401',message)
        self.assertNotIn('private',message)
    def test_untrusted_exception_not_echoed(self):
        self.assertNotIn('secret-token',safe_error(ValueError('secret-token')))
    def test_authored_message_is_visible(self):
        self.assertEqual(safe_error(SafeError('Missing required secret: COVERR_API_KEY')),'Missing required secret: COVERR_API_KEY')
