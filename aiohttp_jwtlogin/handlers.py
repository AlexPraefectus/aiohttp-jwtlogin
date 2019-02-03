import aiohttp.web


async def no_header_default_handler(*args, **kwargs) -> aiohttp.web.Response:
    """
    Default handler called when no header provided in request
    :return: 401 Unauthorized
    """
    return aiohttp.web.Response(text="Unauthorized: please provide auth header", status=401)


async def bad_jwt_default_handler(*args, **kwargs) -> aiohttp.web.Response:
    """
    Default handler called when jwt decoding returned an error
    :return: 403 response
    """
    return aiohttp.web.Response(text="Forbidden: JWT can't be decoded", status=403)


async def user_not_found_default_handler(*args, **kwargs) -> aiohttp.web.Response:
    """
    Default handler called when user loader returned NoneType object
    :return: 403 response
    """
    return aiohttp.web.Response(text="Forbidden: user not found", status=403)


async def jwt_expired_default_handler(*args, **kwargs) -> aiohttp.web.Response:
    """
    Default handler called when JWT expired
    :return: 403 response
    """
    return aiohttp.web.Response(text="Forbidden: token expired", status=403)

