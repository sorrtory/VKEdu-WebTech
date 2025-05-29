import askme_fedukov.settings as settings
import requests
from app.utils.jwt import generate_jwt_token

class Centrifugo:

    def __init__(self, channel: str):
        """
        Initialize Centrifugo with the request object.
        """
        self.channel = channel

    @staticmethod
    def publish_question(id: int):
        """
        Publish a question to a Centrifugo channel.
        """
        channel = f"question:{id}"
        data = {
            "id": id,
            "type": "question",
        }
        return Centrifugo.publish_to(channel, data)

    @staticmethod
    def publish_to(channel: str, data: dict):
        """
        Publish a message to a Centrifugo channel.
        """
        url = f"{settings.CENTRIFUGO_HOST}/api/publish"
        headers = {'Content-type': 'application/json',
                   'X-API-Key': settings.CENTRIFUGO_HTTP_API_KEY}
        payload = {
            "channel": channel,
            "data": data
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    @staticmethod
    def get_sub_jwt(self, user_id: str = ""):
        """
        Generate a JWT token for Centrifugo.
        """
        return generate_jwt_token(str(user_id), 
                                  settings.CENTRIFUGO_HMAC_SECRET_KEY, 
                                  settings.CENTRIFUGO_JWT_EXPIRATION)

    @staticmethod
    def sub_by_cookies(auth):
        """
        Set cookies for JWT token and Centrifugo URL.
        """
        user_id = str(auth.profile.user.id) if auth.authenticated else ""
        auth.new_cookies.update({
            'centrifugo_url': settings.CENTRIFUGO_HOST,
            'centrifugo_jwt': Centrifugo.get_sub_jwt(user_id)
        })
        

class CentrifugoQuestion(Centrifugo):
    """
    Centrifugo class for handling question-related operations.
    """

    def __init__(self, channel: str):
        super().__init__(channel)

    @staticmethod
    def publish_question(id: int):
        """
        Publish a question to a Centrifugo channel.
        """
        return Centrifugo.publish_question(id)