from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    This model represents a user profile.
    Based on Django's User model.
    """
    # questions from Question model
    # question_likes from Question model
    # answers from Answer model
    # answer_likes from Answer model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', 
                               default='avatars/default.png')

    def __str__(self):
        return self.user.username


class Card(models.Model):
    """
    This model represents an abstract card
    """
    author = None
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class QuestionLike(models.Model):
    """
    This model represents a like on a question. Used by many-to-many relationship.
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    question = models.ForeignKey("Question", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'question')


class QuestionManager(models.Manager):
    """
    This is the custom manager for the Question model.
    """

    def hot(self):
        """
        Returns hot questions.
        """
        return self.get_queryset().filter(hot=True)

    def new(self):
        """
        Returns questions ordered by timestamp.
        """
        return self.get_queryset().order_by('-created_at')


class Question(Card):
    """
    This model represents a question card. 
    """
    objects = QuestionManager()

    # title         from Card base class
    # content       from Card base class
    # created_at    from Card base class
    # answers       from Answer model
    # tags          from Tag model
    author = models.ForeignKey(Profile, on_delete=models.CASCADE,
                               related_name='questions')
    likes = models.ManyToManyField(Profile, through='QuestionLike', blank=True,
                                   related_name='question_likes')
    hot = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_answers(self):
        return self.answers.all()

    def get_tags(self):
        return self.tags.all()

    def get_likes_number(self):
        return self.likes.count()

    def is_hot(self):
        """
        Determines if the question is hot based on the number of likes.
        """
        return self.likes.count() > 10

    def update_hot_status(self):
        """
        Updates the hot status of the question.
        Based on .is_hot() method.
        """
        self.hot = self.is_hot()
        self.save()


class AnswerLike(models.Model):
    """
    This model represents a like on an answer. Used by many-to-many relationship.
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'answer')


class Answer(Card):
    """
    This model represents an answer card.
    """
    # title         from Card base class
    # content       from Card base class
    # created_at    from Card base class
    # tags          from Tag model
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='answers')
    likes = models.ManyToManyField(
        Profile, through='AnswerLike', blank=True, related_name='answer_likes')
    question = models.ForeignKey(
        Question, related_name='answers', on_delete=models.CASCADE)


class Tag(models.Model):
    """
    This model represents a tag that can be associated with cards.
    """
    name = models.CharField(max_length=50, unique=True)
    questions = models.ManyToManyField(
        Question, blank=True, related_name='tags')
    answers = models.ManyToManyField(Answer, blank=True, related_name='tags')

    def __str__(self):
        return self.name

    def get_questions(self):
        """
        Returns the questions related to this tag.
        """
        return self.question_set.all()

    def get_answers(self):
        """
        Returns the answers related to this tag.
        """
        return self.answer_set.all()
