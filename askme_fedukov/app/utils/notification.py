import requests

import askme_fedukov.settings as settings

from app.utils.jwt import generate_jwt_token
from app.utils.authentication import Authentication
from app.models import Answer



class Centrifugo:

    def __init__(self, channel: str):
        """
        Initialize Centrifugo with the request object.
        """
        # Channel name for Centrifugo
        self.channel = channel
        # Cookie's name for channel
        self.cookie_channel_name = "centrifugo_channel_default" 
        # Data to be published to the channel
        self.data = {}


    def publish(self):
        """
        Publish data: dict to a Centrifugo channel.
        Returns the response from the Centrifugo API.
        """
        url = f"http://{settings.CENTRIFUGO_HOST}/api/publish"
        headers = {'Content-type': 'application/json',
                   'X-API-Key': settings.CENTRIFUGO_HTTP_API_KEY}
        
        payload = {
            "channel": self.channel,
            "data": self.data
        }

        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def get_sub_jwt(self, user_id: str = ""):
        """
        Generate a JWT token for Centrifugo.
        """
        return generate_jwt_token(str(user_id),
                                  settings.CENTRIFUGO_CLIENT_TOKEN_HMAC_SECRET_KEY,
                                  settings.CENTRIFUGO_JWT_EXPIRATION)
    
    def sub_by_cookies(self, auth:Authentication):
        """
        Update auth.new_cookies with Centrifugo URL and JWT token.
        """
        user_id = ""
        if auth and auth.profile and auth.profile.user:
            user_id = auth.profile.user.id
        
        # Update channel in cookies if it has changed
        if auth.old_cookies.get(self.cookie_channel_name) != self.channel:
            auth.new_cookies[self.cookie_channel_name] = self.channel
        
        # Update Centrifugo settings in cookies
        if auth.old_cookies.get('centrifugo_url') != settings.CENTRIFUGO_HOST:
            auth.new_cookies['centrifugo_url'] = settings.CENTRIFUGO_HOST
        if auth.old_cookies.get('centrifugo_jwt') != self.get_sub_jwt(user_id):
            auth.new_cookies['centrifugo_jwt'] = self.get_sub_jwt(user_id)


class CentrifugoQuestion(Centrifugo):
    """
    Centrifugo class for handling question-related notification.
    """

    def __init__(self, question_id):
        self.question_id = question_id
        channel = f"question:{question_id}"
        super().__init__(channel)
        self.cookie_channel_name = "centrifugo_channel_question"

    def publish_answer(self, answer: Answer):
        """
        Overrides .data with related data and
        publish the question to a Centrifugo channel.
        Returns the response from the Centrifugo API.
        """
        self.data.update({
            "question_id": self.question_id,
            "answer_id": answer.id,
            "answer_content": answer.content, 
            "answer_author": answer.author.user.username,
        })
        return self.publish()
    
class CentrifugoMain(Centrifugo):
    """
    Centrifugo class for handling index page notifications.
    """

    def __init__(self):
        channel = "main"
        super().__init__(channel)
        self.cookie_channel_name = "centrifugo_channel_main"

    def publish(self, msg: str = "Test message"):
        """
        Add message to .data and publish it to the index channel.
        Returns the response from the Centrifugo API.
        """
        self.data["message"] = msg
        return super().publish()
    