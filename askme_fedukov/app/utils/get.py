from app.models import Answer, Question

def get_answer_page_number_by_id(id, cards_per_page: int = 3):
    """
    Returns the page number of the answer by id.
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