import unittest
import aiohttp_jwtlogin as jwtlogin
from aiohttp import web
import sys
from io import StringIO


def not_async_handler(*args, **kwargs):
    pass


async def async_handler(*args, **kwargs):
    pass


class TestExtensionBinding(unittest.TestCase):
    def setUp(self):
        self.empty_config = dict()
        self.minimal_config = {
            'AUTH_HEADER_NAME': 'Authorization',
            'JWT_ENCODING_ALGORITHM': 'HS256',
            'JWT_SECRET_KEY': 'some',
            'JWT_DEFAULT_LIFETIME': 60 * 60 * 24
        }
        self.config_no_coroutine = self.minimal_config.copy()
        # noinspection PyTypeChecker
        self.config_no_coroutine.update({
            'NO_HEADER_CALLBACK': async_handler,
            'BAD_JWT_CALLBACK': not_async_handler,
            'NO_USER_CALLBACK': async_handler,
            'JWT_EXPIRED_CALLBACK': async_handler,
            'USER_LOADER': async_handler
        })
        self.correct_config = self.config_no_coroutine.copy()
        # noinspection PyTypeChecker
        self.correct_config['BAD_JWT_CALLBACK'] = async_handler
        self.app = web.Application()

    def test_empty_config(self):
        with self.assertRaises(KeyError):
            ext = jwtlogin.JWTLogin(self.empty_config)

    # def test_minimal_config(self):
    #     """
    #     working only when running as a single test for some reason
    #     :return:
    #     """
    #     old_stderr = sys.stderr
    #     warnings = StringIO()
    #     sys.stderr = warnings
    #     ext = jwtlogin.JWTLogin(self.minimal_config)
    #     sys.stderr = old_stderr
    #     print(warnings.getvalue().split('\n'))
    #     self.assertTrue(all([param in warnings.getvalue() for param, i in jwtlogin.JWTLogin._callbacks_lst]))

    def test_config_w_sync_callback(self):
        with self.assertRaises(ValueError):
            ext = jwtlogin.JWTLogin(self.config_no_coroutine)

    def test_correct_config(self):
        old_stderr = sys.stderr
        warnings = StringIO()
        sys.stderr = warnings
        ext = jwtlogin.JWTLogin(self.correct_config)
        ext.bind(self.app)
        sys.stderr = old_stderr
        self.assertEqual(len(warnings.getvalue()), 0)
        self.assertIsNotNone(self.app['jwtlogin'])


if __name__ == "__main__":
    unittest.main()
