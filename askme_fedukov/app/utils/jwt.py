import jwt
import time
import askme_fedukov.settings as settings

def generate_jwt_token(user_id: str="", 
                       secret:str = settings.SECRET_KEY, 
                       expiration: int = 3600) -> str:
    """
    Generate a JWT token from Centrifugo HMAC for user or anonymous user.
    """
    claims = {"sub": user_id, "exp": int(time.time()) + settings.CENTRIFUGO_JWT_EXPIRATION}
    token = jwt.encode(claims, settings.CENTRIFUGO_CLIENT_TOKEN_HMAC_SECRET_KEY , algorithm="HS256")
    return token

def check_jwt_token(request, cookie_name) -> bool:
    """
    Check the JWT token in the request cookies if it exists.
    """
    jwt_token = request.COOKIES.get(cookie_name, None)
    if jwt_token is not None:
        try:
            # Decode the JWT to check its validity
            jwt.decode(jwt_token, settings.CENTRIFUGO_CLIENT_TOKEN_HMAC_SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    return True if jwt_token else False
