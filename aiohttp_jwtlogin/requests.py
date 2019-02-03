from aiohttp import web


class RequestWithJWT(web.Request):
    """Can be used for type hinting. Has additional property token"""
    @property
    def token(self) -> dict:
        return dict()


class RequestWithUser(RequestWithJWT):
    """Can be user for type hinting. Has additional properties token and user"""
    @property
    def user(self):
        return None
