import jwt
from aiohttp import web
from aiohttp_jwtlogin import JWTLogin, jwt_required, user_required
import datetime

users = [(f'user{i}', f'password{i}') for i in range(10)]


async def user_loader(token: dict):
    for login, password in users:
        if login == token['login']:
            return login, password
    return None


cfg = {
    'AUTH_HEADER_NAME': 'Authorization',
    'JWT_ENCODING_ALGORITHM': 'HS256',
    'JWT_SECRET_KEY': 'keep-it-secret',
    'JWT_DEFAULT_LIFETIME': 60 * 60 * 24 * 7,
    'NO_HEADER_CALLBACK': None,
    'BAD_JWT_CALLBACK': None,
    'NO_USER_CALLBACK': None,
    'USER_LOADER': user_loader}

app = web.Application()
JWTLogin(app, cfg)

token = app['jwtlogin'].encode({'login': 'user1',
                                'password': 'password1',
                                'iat': datetime.datetime.utcnow(),
                                'exp': datetime.datetime.utcnow() +
                                datetime.timedelta(seconds=cfg['JWT_DEFAULT_LIFETIME'])})


@jwt_required
async def i_need_jwt(request: web.Request):
    return web.Response(text='Wow, I\'ve got a token' + str(request.token))


@jwt_required
@user_required
async def i_need_user(request: web.Request):
    return web.Response(text='Wow, I\'ve got a user' + str(request.user))


app.router.add_get('/need-jwt/', i_need_jwt)
app.router.add_get('/need-usr/', i_need_user)

if __name__ == "__main__":
    web.run_app(app)
