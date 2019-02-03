# Aiohttp-jwtlogin

[![codecov](https://codecov.io/gh/AlexPraefectus/aiohttp-jwtlogin/branch/master/graph/badge.svg?token=aTVYKRaKBn)](https://codecov.io/gh/AlexPraefectus/aiohttp-jwtlogin)
[![Build Status](https://travis-ci.com/AlexPraefectus/aiohttp-jwtlogin.svg?token=GdQGmA44KMV9yxt3fEzN&branch=master)](https://travis-ci.com/AlexPraefectus/aiohttp-jwtlogin)

## What is Aiohttp-jwtlogin?

Extension to handle user authentication using JSON Web Tokens also known as JWT. Aiohttp-jwtlogin uses [PyJWT](https://github.com/jpadilla/pyjwt) to deal with JWT encoding & decoding

## What does Aiohttp-jwtlogin offer to developers?

- shortcuts to encode & decode tokens
- @jwt_required and @user_required decorators to protect view functions
- making some work for You to avoid boilerplate code


## How to work with it?

### Initializing
Some config keys are necessary for correct work, some are optional. In the following examples only necessary variables provided

```python
from aiohttp_jwtlogin import JWTLogin
from aiohttp import web

cfg ={
    'AUTH_HEADER_NAME': 'Authorization',  # this name is common but You can provide your own
    'JWT_ENCODING_ALGORITHM': 'HS256',  # check available algorithms in PyJWT package
    'JWT_SECRET_KEY': 'keep-it-secret',  # key to encode/decode the token
    'JWT_DEFAULT_LIFETIME': 60 * 60 * 24 * 7,  # how long token is valid by default (in seconds)
}

app = web.Application()
ext = JWTLogin(cfg)
ext.bind(app)  # after this the extension class object is available as app['jwtlogin']
```

### Protecting views with decorators
```python
from aiohttp_jwtlogin import jwt_required
from aiohttp import web


@jwt_required
async def view_that_needs_jwt(request: web.Request):
    token = request.token  # dict containing decoded jwt payload
    return web.Response(text='some')
```

@user_required decorator is not available at this point. Extension does not know where and how do You prefer to store users' information so You should teach it how to load your users

```python
async def load_user(token: dict) -> YourUserClass:
    ### do something
    return some_user
    
    
cfg = {
    ### some other options
    'USER_LOADER': load_user 
    ### some other options    
}

@jwt_required
@user_required
async def view_with_loaded_user(request):
    user = request.user  # way to access loaded user
    token = request.token  # token still available 
```

## What does Aiohttp-jwtlogin checks?

* Request should contain header AUTH_HEADER_NAME. If header is not present than NO_HEADER_CALLBACK will be called instead of view function (default returns 401 and a human-readable message). Possible header formats:
  * AUTH_HEADER_NAME: Bearer TOKEN
  * AUTH_HEADER_NAME: TOKEN
  * The most canonical: "Authorization: Bearer Token"
  
* Token contained in the header is not expired or JWT_EXPIRED_CALLBACK will be called instead of view function
* Token can be properly decoded or BAD_JWT_CALLBACK will be called
* If view is decorated with @user_required than NO_USER_CALLBACK will be called in case when USER_LOADER returned None




