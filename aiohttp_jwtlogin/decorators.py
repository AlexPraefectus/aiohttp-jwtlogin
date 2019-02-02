from functools import wraps
import jwt
from aiohttp_jwtlogin import JWTLogin


def jwt_required(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        print(len(args))
        request = args[0]
        ext: JWTLogin = request.app['jwtlogin']
        auth_header = request.headers.get('authorization')
        if not auth_header:
            return await ext._no_header(*args, **kwargs)
        try:
            request.token = ext.decode(request.headers['authorization'])
            print(request.token)
        except jwt.ExpiredSignatureError:
            return await ext._jwt_expired(*args, **kwargs)
        except jwt.InvalidTokenError:
            return await ext._bad_jwt(*args, **kwargs)
        return await f(*args, **kwargs)
    return wrapper


@jwt_required
def user_required(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        pass
        return await f(*args, **kwargs)
    return wrapper
