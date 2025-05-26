from app.models import AnswerLike, QuestionLike, Answer, Question
from app.utils.authentication import Authentication
from django.http import HttpRequest

from .get import get_userlike_status_and_count_for

import json


class Like:

    def __init__(self, auth: Authentication, request: HttpRequest, model_type: str, id: int):
        """
        Initializes the Like object with authentication, model type, and model ID.
        """
        self.auth = auth
        self.body = {}

        # Parse JSON body if POST and content-type is application/json
        if request.method == "POST" and request.content_type == "application/json":
            try:
                self.body = json.loads(request.body)
            except Exception as e:
                self.body = {}
        else:
            self.body = {}

        self.params = request.GET

        model_mapping = {
            "explore": Question,
            "main": Question,
            "question": Question,
            "answer": Answer,
        }

        self.model = model_mapping.get(model_type)
        self.model_id = id

        like_mapping = {
            Question: QuestionLike,
            Answer: AnswerLike,
        }
        self.like_model = like_mapping.get(self.model)

        self.like_action = self.body.get('like_action')
        self.like_type = self.body.get('like_type')

    def put_like(self):
        """
        Creating a new like or updating its type to "dislike" or "like".
        """
        obj, created = self.like_model.objects.get_or_create(
            user=self.auth.profile,
            **{f"{self.model.__name__.lower()}_id": self.model_id},
            defaults={'is_dislike': (self.like_type == "dislike")}
        )
        if not created:
            obj.is_dislike = (self.like_type == "dislike")
            obj.save()

        return "Like created." if created else "Like updated."

    def delete_like(self):
        """
        Deletes the like for the given model type and ID.
        """
        try:
            like = self.like_model.objects.get(
                user=self.auth.profile,
                **{f"{self.model.__name__.lower()}_id": self.model_id}
            )
            like.delete()
            return "Like deleted."
        except self.like_model.DoesNotExist:
            return "Like does not exist."

    def process(self):
        """
        Processes the like action based on the request data.
        """
        action = None
        if self.like_action == "put":
            action = self.put_like()
        elif self.like_action == "delete":
            action = self.delete_like()

        status, new_count = get_userlike_status_and_count_for(
            self.auth, self.model, self.model_id)
        if status is None:
            return {
                "status": "error",
                "message": "Like action failed. Model not found or invalid.",
                "card_id": self.model_id,
                "model_type": self.model.__name__.lower() if self.model else None
            }
        return {
            "status": "success",
            "message": action if action else "No action performed.",
            "card_id": self.model_id,
            "model_type": self.model.__name__.lower() if self.model else None,
            "like_status": status,
            "like_count": new_count
        }

    def check_request(self):
        """
        Checks if the request is valid for liking

        Scheme for POST request:
        {
            "like_type": "like" or "dislike",
            "like_action": "put" or "delete"
        }
        Raises Http404 if the request is invalid.
        """

        if self.body == {}:
            return "Invalid request. POST data is required."
        # Check params
        if not self.auth.authenticated:
            return "User must be authenticated to like."
        if not self.model_id:
            return "Model ID is required."
        if self.model is None or self.model not in [Question, Answer]:
            return "Invalid model type. Must be 'question' or 'answer'."

        # Check schema
        if self.body.get('like_type') not in ['like', 'dislike']:
            return "Invalid like action. Must be 'like' or 'dislike'."
        if self.body.get('like_action') not in ["put", "delete"]:
            return "Invalid like action. Must be 'put' or 'delete'."

        return None  # No errors, request is valid
