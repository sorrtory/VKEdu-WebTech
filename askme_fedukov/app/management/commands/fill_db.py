from django.core.management.base import BaseCommand
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from django.contrib.auth.models import User
from django.utils.timezone import now
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Fill the database with sample data based on the given ratio'

    def add_arguments(self, parser):
        # Adds a custom argument 'ratio' to the command
        parser.add_argument('ratio', type=int, help='The ratio of records to create')

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(f'Starting to fill the database with a ratio of {ratio}')

        self.create_test_user()
        self.create_users(ratio)
        self.create_tags(ratio)
        self.create_questions(ratio)
        self.create_answers(ratio)
        self.create_likes(ratio)

        self.stdout.write(self.style.SUCCESS(f'Successfully filled the database with test data'))

    def create_test_user(self):
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'testuser@example.com', 'password': 'testpassword'}
        )
        if created:
            Profile.objects.create(user=test_user)

    def create_users(self, ratio):
        for _ in range(ratio):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password'
            )
            Profile.objects.create(user=user)

    def create_tags(self, ratio):
        for _ in range(ratio):
            Tag.objects.create(name=fake.word())

    def create_questions(self, ratio):
        profiles = list(Profile.objects.all())
        tags = list(Tag.objects.all())
        for _ in range(ratio * 10):
            question = Question.objects.create(
                author=random.choice(profiles),
                title=fake.sentence(),
                content=fake.text(),
                created_at=now()
            )
            question.tags.set(random.sample(tags, min(len(tags), random.randint(1, 3))))

    def create_answers(self, ratio):
        profiles = list(Profile.objects.all())
        questions = list(Question.objects.all())
        for _ in range(ratio * 100):
            Answer.objects.create(
                author=random.choice(profiles),
                question=random.choice(questions),
                content=fake.text(),
                created_at=now()
            )

    def create_likes(self, ratio):
        profiles = list(Profile.objects.all())
        questions = list(Question.objects.all())
        answers = list(Answer.objects.all())

        for _ in range(ratio * 200):
            if random.choice([True, False]):
                QuestionLike.objects.get_or_create(
                    user=random.choice(profiles),
                    question=random.choice(questions)
                )
            else:
                AnswerLike.objects.get_or_create(
                    user=random.choice(profiles),
                    answer=random.choice(answers)
                )
