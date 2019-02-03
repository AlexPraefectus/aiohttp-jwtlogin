from functools import wraps
import jwt
from aiohttp_jwtlogin import JWTLogin


def jwt_required(f):
    """
    Tries to decode JWT containing in provided AUTH_HEADER_NAME header
    Returns error callbacks instead of original request handler if something went wrong
    Returns original handler with token available as request.token (dict) if JWT decoding succeeded
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        # print('jwt-required')
        request = args[0]
        ext: JWTLogin = request.app['jwtlogin']
        auth_header = request.headers.get('authorization')
        if not auth_header:
            return await ext._no_header(*args, **kwargs)
        try:
            # print(request.headers['authorization'])
            request.token = ext.decode(request.headers['authorization'].split()[-1])
        except jwt.ExpiredSignatureError:
            return await ext._jwt_expired(*args, **kwargs)
        except jwt.InvalidTokenError:
            return await ext._bad_jwt(*args, **kwargs)
        return await f(*args, **kwargs)
    return wrapper


# @jwt_required
def user_required(f):
    """
    Loads user with provided user_loader callback
    user available as request.user
    this decorator should be used together with jwt_required
    order:
        @jwt_required
        @user_required
        async def request_handler()
    Returns
    """
    @wraps(f)
    async def wrapper(*args, **kwargs):
        # print('user-required')
        request = args[0]
        ext: JWTLogin = request.app['jwtlogin']
        request.user = await ext.user_loader(request.token)
        if not request.user:
            return await ext._user_not_found(*args, **kwargs)
        return await f(*args, **kwargs)
    return wrapper
