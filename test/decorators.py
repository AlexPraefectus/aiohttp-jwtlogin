from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp_jwtlogin import JWTLogin, jwt_required, user_required


class DecoratorsTest(AioHTTPTestCase):

    async def get_application(self):
        @jwt_required
        async def protected_view(request):
            return web.Response(text=str(request.token), status=200)

        @jwt_required
        @user_required
        async def view_with_user(request):
            return web.Response(text=request.user)

        async def user_loader(token: dict):
            # print(token.get('user'))
            return token.get('user')

        self.minimal_config = {
            'AUTH_HEADER_NAME': 'Authorization',
            'JWT_ENCODING_ALGORITHM': 'HS256',
            'JWT_SECRET_KEY': 'some',
            'JWT_DEFAULT_LIFETIME': 60 * 60 * 24,
            'USER_LOADER': user_loader,
        }

        app = web.Application()
        self.jwt = JWTLogin(self.minimal_config)
        self.jwt.bind(app)
        app.router.add_get('/jwt/', protected_view)
        app.router.add_get('/usr/', view_with_user)

        self.header_correct_no_usr = {'Authorization': 'Bearer {}'.format(self.jwt.encode({'some': 'some'},
                                                                                          lifetime=60 * 60 * 24))}
        self.header_correct = {'Authorization': 'Bearer {}'.format(self.jwt.encode({'user': 'User'},
                                                                                   lifetime=60 * 60 * 24))}
        self.header_empty = dict()
        self.header_w_expired = {'Authorization': 'Bearer {}'.format(self.jwt.encode({'some': 'some'},
                                                                                     lifetime=-60 * 60 * 24))}
        self.header_incorrect = {'Authorization': 'Bearer I_AM_NOT_JSON_WEB_TOKEN'}

        return app

    @unittest_run_loop
    async def test_request_no_header(self):
        resp1 = await self.client.request("GET", '/jwt/', headers=self.header_empty)
        self.assertEqual(resp1.status, 401)
        resp2 = await self.client.request("GET", '/usr/', headers=self.header_empty)
        self.assertEqual(resp2.status, 401)

    @unittest_run_loop
    async def test_bad_jwt(self):
        resp1 = await self.client.request("GET", '/jwt/', headers=self.header_incorrect)
        self.assertEqual(resp1.status, 403)
        self.assertTrue("can't be decoded" in await resp1.text())
        resp2 = await self.client.request("GET", '/usr/', headers=self.header_incorrect)
        self.assertEqual(resp2.status, 403)
        self.assertTrue("can't be decoded" in await resp2.text())

    @unittest_run_loop
    async def test_jwt_expired(self):
        resp1 = await self.client.request("GET", '/jwt/', headers=self.header_w_expired)
        self.assertEqual(resp1.status, 403)
        resp2 = await self.client.request("GET", '/usr/', headers=self.header_w_expired)
        self.assertEqual(resp2.status, 403)

    @unittest_run_loop
    async def test_user_not_found(self):
        resp1 = await self.client.request("GET", '/jwt/', headers=self.header_correct_no_usr)
        self.assertEqual(resp1.status, 200)
        resp2 = await self.client.request("GET", '/usr/', headers=self.header_correct_no_usr)
        self.assertEqual(resp2.status, 403)

    @unittest_run_loop
    async def test_all_ok(self):
        correct_token = self.jwt.encode({'user': 'some user object'}, lifetime=60 * 60 * 24)
        self.header_correct['Authorization'].format(correct_token)
        resp1 = await self.client.request("GET", '/jwt/', headers=self.header_correct)
        # print(await resp1.text())
        self.assertEqual(resp1.status, 200)
        resp2 = await self.client.request("GET", '/usr/', headers=self.header_correct)
        self.assertEqual(resp2.status, 200)
