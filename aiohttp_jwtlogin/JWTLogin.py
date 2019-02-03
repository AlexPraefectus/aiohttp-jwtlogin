import aiohttp.web
from .handlers import (bad_jwt_default_handler,
                       user_not_found_default_handler,
                       no_header_default_handler,
                       jwt_expired_default_handler)
import inspect
import datetime
import jwt
import logging


class JWTLogin:
    """
    aiohttp-jwtlogin extension class
    """
    _no_header = no_header_default_handler
    _bad_jwt = bad_jwt_default_handler
    _user_not_found = user_not_found_default_handler
    _jwt_expired = jwt_expired_default_handler

    _callbacks_lst = [  # (PARAM_NAME, attr_name
        ("NO_HEADER_CALLBACK", "_no_header"),
        ("BAD_JWT_CALLBACK", "_bad_jwt"),
        ("NO_USER_CALLBACK", "_user_not_found"),
        ("JWT_EXPIRED_CALLBACK", "_jwt_expired"),
        ("USER_LOADER", "user_loader")
    ]

    def encode(self, payload: dict, lifetime=None) -> bytes:
        if not lifetime:
            lifetime = self.JWT_DEFAULT_LIFETIME
        payload['iat'] = datetime.datetime.utcnow()
        payload['exp'] = payload['iat'] + datetime.timedelta(seconds=lifetime)
        return jwt.encode(payload,
                          self.JWT_SECRET_KEY,
                          algorithm=self.JWT_ENCODING_ALGORITHM)

    def decode(self, token: str) -> dict:
        """
        Shortcut to avoid boilerplate code
        See PyJWT.decode() for details
        :param token: JWT
        :return: dict
        """
        return jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.JWT_ENCODING_ALGORITHM])

    def _set_callbacks(self, config: dict):
        """
        checking & setting callback funcs if present in config
        :param config:
        :return: None
        """
        for callback, attr_name in JWTLogin._callbacks_lst:
            cb = config.get(callback)
            if not cb:
                logging.warning(f"{callback} not provided")
            else:
                if not inspect.iscoroutinefunction(cb):
                    raise ValueError(f"{callback} should be a coroutine")
                setattr(self, attr_name, cb)

    def __init__(self, app: aiohttp.web.Application, config: dict):
        """
        Binding extension object to the application
        :param app: application to bind extension on
        :param config:
            required keys:
                AUTH_HEADER_NAME - header with JWT
                JWT_ENCODING_ALGORITHM - check PyJWT package to get actual list of available algorithms
                    algorithms (list can be outdated): HS256, HS384, HS512, ES256, ES384, ES512, RS256, RS384, RS512, PS256, PS384, PS512
                JWT_DEFAULT_LIFETIME (seconds)
                JWT_SECRET_KEY - key to DECODE token. Important in case of using asymmetric encoding algorithms
            optional keys:
                NO_HEADER_CALLBACK - coroutine called instead of request handler when no auth header provided
                BAD_JWT_CALLBACK - coroutine called instead of request handler when JWT decoding returned an error
                NO_USER_CALLBACK - coroutine called instead of request handler when user loader returned None
                JWT_EXPIRED_CALLBACK - coroutine called instead of request handler when
                USER_LOADER - coroutine callback to load user from jwt
                    signature: async def user_loader(jwt: dict) -> Optional[YourUserClass]
        """
        app['jwtlogin'] = self
        self.HEADER_NAME = config['AUTH_HEADER_NAME']
        self.JWT_ENCODING_ALGORITHM = config['JWT_ENCODING_ALGORITHM']
        self.JWT_SECRET_KEY = config['JWT_SECRET_KEY']
        self.JWT_DEFAULT_LIFETIME = config['JWT_DEFAULT_LIFETIME']
        self._set_callbacks(config)




