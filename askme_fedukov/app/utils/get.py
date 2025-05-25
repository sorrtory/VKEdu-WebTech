# This file contains utility functions,
# which are used to retrieve data from the database

from app.models import Answer, Question, AnswerLike, QuestionLike

from app.utils.authentication import Authentication
from app.utils.feed import PaginatedFeed
from app.utils.frontend_models import CardAnswer, CardExplore, BadgeTag, CardMain

from django.core.paginator import Paginator
from django.db.models import Count


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
    questions = Question.objects.new().prefetch_related(
        'tags').annotate(like_count=Count('likes'))
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
            question.like_count
        )
        for question in questions
    ]
    return PaginatedFeed(auth, Paginator(cards, cards_per_page)).on_page(page_number)


def get_feed_answers(auth: Authentication, question_id: int, page_number: int, cards_per_page: int = 3):
    """
    Returns a paginator of CardAnswer objects filtered by question id.
    """
    answers = Answer.objects.filter(question_id=question_id).prefetch_related(
        'tags').annotate(like_count=Count('likes'))
    cards = [
        CardAnswer(
            auth,
            answer.id,
            answer.author,
            get_userlike_status_for(auth, Answer, answer.id),
            answer.content,
            [BadgeTag(tag.name, tag.type) for tag in answer.tags.all()],
            answer.like_count
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
            question.likes.count()
        )
        return card
    except Question.DoesNotExist:
        return None


def get_feed_hot(auth: Authentication, page_number: int, cards_per_page: int = 3):
    """
    Returns a paginator of CardExplore objects representing hot questions.
    """

    questions = Question.objects.hot().prefetch_related(
        'tags').annotate(like_count=Count('likes'))
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
            question.like_count
        )
        for question in questions
    ]
    return PaginatedFeed(auth, Paginator(cards, cards_per_page)).on_page(page_number)


def get_questions_by_tag(auth: Authentication, tag_name: str, page_number: int, cards_per_page: int = 3):
    """
    Returns a paginator of CardExplore objects filtered by tag name.
    """

    questions = Question.objects.filter(tags__name=tag_name).prefetch_related(
        'tags').annotate(like_count=Count('likes'))
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
            question.like_count
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
        like = model_like.objects.filter(user=auth.profile, id=id)
        if like.exists():
            like_instance = like.first()
            if like_instance.is_dislike:
                return -1
            return 1
        else:
            return 0
    except model.DoesNotExist:
        return None
    
