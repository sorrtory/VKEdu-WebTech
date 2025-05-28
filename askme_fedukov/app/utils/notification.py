import jwt
import time
import askme_fedukov.settings as settings


def generate_jwt_token(user_id: str) -> str:
    """
    """
    claims = {"sub": str(user_id), "channel": "$gossips", "exp": int(time.time()) + settings.CENTRIFUGO_JWT_EXPIRATION}
    token = jwt.encode(claims, settings.CENTRIFUGO_SECRET , algorithm="HS256")
    return token

def register_jwt_token(token):
    """
    Call centrifugo to register the JWT token for the user.
    """
    import requests
    url = f"{settings.CENTRIFUGO_HOST}/api/jwt"
    headers = {
        "Content-Type": "application/json",
        "Authorization:  

def check_jwt_token(request):
    """
    Check the JWT token in the request cookies if it exists.
    """
    jwt_token = request.COOKIES.get('jwttoken', None)
    if jwt_token is not None:
        try:
            # Decode the JWT to check its validity
            jwt.decode(jwt_token, settings.CENTRIFUGO_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    return True if jwt_token else False


def add_auth_cookies(auth, response):
    """
    Set cookies for JWT token and Centrifugo URL.
    """
    if auth.jwt_updated:
        response.set_cookie("jwttoken", auth.jwt_token)
    if not auth.request.COOKIES.get('centrifugo', None):
        response.set_cookie("centrifugourl", settings.CENTRIFUGO_HOST)
    return response