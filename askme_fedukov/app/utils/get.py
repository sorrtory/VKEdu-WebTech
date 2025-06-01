# This file contains utility functions,
# which are used to retrieve data from the database

# TODO: Split this fucking horror into classes. I have no idea what's going on here.
# Also json parser should be here instead of database queries (which have to be connected with view classes).

import json
from app.models import Answer, Question, AnswerLike, QuestionLike

from app.utils.authentication import Authentication
from app.utils.feed import PaginatedFeed
from app.utils.frontend_models import CardAnswer, CardExplore, BadgeTag, CardMain

from django.core.paginator import Paginator


def get_answer_page_number_by_id(id: int, cards_per_page: int = 3):
    """
    Returns the page number of the answer by its id.
    """
    try:
        answer = Answer.objects.get(id=id)
        question = answer.question
        page_number = (question.answers.count() - 1) // cards_per_page + 1
        return page_number
    except Answer.DoesNotExist:
        return None
    except Question.DoesNotExist:
        return None


def get_feed_explore(auth: Authentication, page_number: int, cards_per_page: int = 3):
    """
    Returns a paginator of CardExplore objects.
    """
    questions = Question.objects.new().prefetch_related('tags')
    cards = [
        CardExplore(
            auth,
            question.id,
            question.author,
            get_userlike_status_for(auth, Question, question.id),
            question.answers.all(),
            question.title,
            question.content,
            [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
            Question.real_likes_by_id(question.id)
        )
        for question in questions
    ]
    return PaginatedFeed(auth, Paginator(cards, cards_per_page)).on_page(page_number)


def get_feed_answers(auth: Authentication, question_id: int, page_number: int, cards_per_page: int = 3):
    """
    Returns a paginator of CardAnswer objects filtered by question id.
    """
    answers = Answer.objects.filter(question_id=question_id).prefetch_related('tags')
    cards = [
        CardAnswer(
            auth,
            answer.id,
            answer.author,
            get_userlike_status_for(auth, Answer, answer.id),
            answer.content,
            [BadgeTag(tag.name, tag.type) for tag in answer.tags.all()],
            Answer.real_likes_by_id(answer.id),
            answer.is_correct,
            not get_checkbox_status_for(auth, answer.id)
        )
        for answer in answers
    ]
    return PaginatedFeed(auth, Paginator(cards, cards_per_page)).on_page(page_number)


def get_question_by_id(auth: Authentication, id: int):
    """
    Returns a CardMain object filled with question data.
    """
    try:
        question = Question.objects.get(id=id)
        card = CardMain(
            auth,
            question.id,
            question.author,
            get_userlike_status_for(auth, Question, question.id),
            question.title,
            question.content,
            [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
            Question.real_likes_by_id(question.id)
        )
        return card
    except Question.DoesNotExist:
        return None


def get_feed_hot(auth: Authentication, page_number: int, cards_per_page: int = 3):
    """
    Returns a paginator of CardExplore objects representing hot questions.
    """

    questions = Question.objects.hot().prefetch_related('tags')
    cards = [
        CardExplore(
            auth,
            question.id,
            question.author,
            get_userlike_status_for(auth, Question, question.id),
            question.answers.all(),
            question.title,
            question.content,
            [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
            Question.real_likes_by_id(question.id)
        )
        for question in questions
    ]
    return PaginatedFeed(auth, Paginator(cards, cards_per_page)).on_page(page_number)


def get_questions_by_tag(auth: Authentication, tag_name: str, page_number: int, cards_per_page: int = 3):
    """
    Returns a paginator of CardExplore objects filtered by tag name.
    """

    questions = Question.objects.filter(tags__name=tag_name).prefetch_related('tags')
    cards = [
        CardExplore(
            auth,
            question.id,
            question.author,
            get_userlike_status_for(auth, Question, question.id),
            question.answers.all(),
            question.title,
            question.content,
            [BadgeTag(tag.name, tag.type) for tag in question.tags.all()],
            Question.real_likes_by_id(question.id)
        )
        for question in questions
    ]
    return PaginatedFeed(auth, Paginator(cards, cards_per_page)).on_page(page_number)


def get_userlike_status_for(auth: Authentication, model: Question | Answer, id: int) -> int:
    """
    Returns the like status for a question.

    int: 
        1 if the user has liked the card,
        0 if the user has not liked the card,
        -1 if the user has disliked the card.
    """
    like_mapping = {Question: QuestionLike, Answer: AnswerLike}
    model_like = like_mapping[model]
    try:
        like = model_like.objects.filter(
            user=auth.profile,
            **{f"{model.__name__.lower()}_id": id},
        )
        if like.exists():
            like_instance = like.first()
            if like_instance.is_dislike:
                return -1
            return 1
        else:
            return 0
    except model.DoesNotExist:
        return None
    
def get_like_count_for(model: Question | Answer, id: int) -> int:
    """
    Returns the like count for a question or answer.

    Returns:
        int: The number of likes.
    """
    return model.real_likes_by_id(id) 

def get_userlike_status_and_count_for(auth: Authentication, model: Question | Answer, id: int) -> tuple[int, int]:
    """
    Returns the like status and like count for a question or answer.

    Returns:
        tuple[int, int]: (like_status, like_count)
    """
    like_status = get_userlike_status_for(auth, model, id)
    like_count = get_like_count_for(model, id)
    return like_status, like_count


def get_checkbox_status_for(auth: Authentication, answer_id: int) -> bool:
    """
    Returns the checkbox status for the answer.

    Returns:
        bool: True if the viewer is the author of the answer's question, False otherwise.
    """
    answ = Answer.objects.filter(id=answer_id).first()
    if answ:
        return answ.question.author == auth.profile
    else:
        return None
    
def get_questions_by_text(query: str):
    """
    Searches for questions by title.
    Returns:
        QuerySet: A queryset of questions that match the title.
    """
    return Question.objects.search(query)


def get_json_data_from_request(request):
    """
    Parses JSON data from the request body.
    
    Returns:
        dict: Parsed JSON data.
    """
    out = {}
    if request.method == "POST" and request.content_type == "application/json":
        try:
            out = json.loads(request.body)
        except Exception as e:
            out = {}
    else:
        raise ValueError("Request method must be POST and content type must be application/json.")

    return out