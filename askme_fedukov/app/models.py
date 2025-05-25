from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class ProfileManager(models.Manager):
    """
    This is the custom manager for the Profile model.
    """

    def get_best_members(self):
        """
        Returns the best members based on the number of questions and answers.
        """
        return self.annotate(
            num_questions=models.Count('questions'),
            num_answers=models.Count('answers')
        ).order_by('-num_answers', '-num_questions')[:5]

    def get_test_profile(self):
        """
        Returns the test profile.
        Should always be in database. See fil_db.py/create_test_profile()
        """
        return self.get_queryset().get(user__username='testuser')

    def create_user(self, username, email, password, avatar=None):
        """
        Creates a new profile.
        """
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        if created:
            user.set_password(password)
            user.save()
            if avatar:
                profile, created = self.get_or_create(
                    user=user, defaults={'avatar': avatar})
            else:
                profile, created = self.get_or_create(user=user)
            if not created:
                return None
            return profile
        return None


def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'


class Profile(models.Model):  # Can also derive from AbstractBaseUser
    """
    This model represents a user profile.
    Based on Django's User model.
    """
    objects = ProfileManager()
    # questions from Question model
    # question_likes from Question model
    # answers from Answer model
    # answer_likes from Answer model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_avatar_path,
                               default='avatars/default.png')

    def __str__(self):
        return self.user.username

    @property
    def tags(self):
        """
        Returns a queryset of all unique tags used by this user in questions and answers.
        """
        question_tags = Tag.objects.filter(questions__author=self)
        answer_tags = Tag.objects.filter(answers__author=self)
        return Tag.objects.filter(Q(id__in=question_tags) | Q(id__in=answer_tags)).distinct()


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
    is_dislike = models.BooleanField(default=False,
                                     help_text="True for dislike, False for like")

    class Meta:
        unique_together = ('user', 'question')


class QuestionManager(models.Manager):
    """
    This is the custom manager for the Question model.
    """

    def update_hot_status(self):
        """
        Updates the hot status of all questions.
        """
        for question in self.get_queryset():
            question.update_hot_status()

    def hot(self):
        """
        Returns hot questions.
        """
        return self.get_queryset().filter(tags__name='hot')

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

    def __str__(self):
        return self.title

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
        hot_tag = Tag.objects.get(name='hot')
        if self.is_hot():
            self.tags.add(hot_tag)
        else:
            self.tags.remove(hot_tag)


class AnswerLike(models.Model):
    """
    This model represents a like on an answer. Used by many-to-many relationship.
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    answer = models.ForeignKey("Answer", on_delete=models.CASCADE)
    is_dislike = models.BooleanField(default=False,
                                     help_text="True for dislike, False for like")
    # TODO make sure to migrate
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
    author = models.ForeignKey(Profile,
                               on_delete=models.CASCADE, related_name='answers')
    likes = models.ManyToManyField(Profile,
                                   through='AnswerLike', blank=True, related_name='answer_likes')
    question = models.ForeignKey(Question,
                                 related_name='answers', on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class TagManager(models.Manager):
    def get_hot_tags(self):
        """
        Returns tags by number of questions.
        """
        return self.annotate(num_questions=models.Count('questions')).order_by('-num_questions')[:8]


class Tag(models.Model):
    """
    This model represents a tag that can be associated with cards.
    """
    objects = TagManager()
    TAG_CHOICES = (
        (0, "primary"),  # default
        (1, "danger"),   # hot
        (2, "success"),  #
        (3, "warning"),  #
        (4, "info"),     #
        (5, "dark")      #
    )
    name = models.CharField(max_length=50, unique=True)
    type = models.PositiveSmallIntegerField(choices=TAG_CHOICES, default=0)
    questions = models.ManyToManyField(Question,
                                       blank=True, related_name='tags')
    answers = models.ManyToManyField(Answer,
                                     blank=True, related_name='tags')

    def __str__(self):
        return self.name
