from django.core.management.base import BaseCommand
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from django.contrib.auth.models import User
from django.utils.timezone import now
from faker import Faker
import random
from tqdm import tqdm

fake = Faker()

class Command(BaseCommand):
    help = 'Fill the database with sample data based on the given ratio'

    def add_arguments(self, parser):
        # Adds a custom argument 'ratio' to the command
        parser.add_argument('ratio', type=int, help='The ratio of records to create')

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(f'Starting to fill the database with a ratio of {ratio}')

        with tqdm(total=5, desc="Filling DB", unit="step") as pbar:
            self.create_test_user()
            pbar.update(1)

            self.create_users(ratio)
            pbar.update(1)

            self.create_tags(ratio)
            pbar.update(1)

            self.create_questions(ratio)
            pbar.update(1)

            self.create_answers(ratio)
            self.create_likes(ratio)
            pbar.update(1)

        self.stdout.write(self.style.SUCCESS(f'Successfully filled the database with test data'))

    def create_test_user(self):
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'testuser@example.com'}
        )
        if created:
            test_user.set_password('testpassword')
            test_user.save()
            # Create a test profile for the test user
            Profile.objects.create(user=test_user)

    def create_users(self, ratio):
        for _ in range(ratio):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password',
            )
            avatar = random.choice(['avatars/default.png', 'avatars/avatar1.webp', 'avatars/avatar2.jpg'])
            Profile.objects.create(user=user, avatar=avatar)

    def create_tags(self, ratio):
        # See models.Tag.TAG_CHOICES
        Tag.objects.get_or_create(name='hot', type=1) # Make sure 'hot' tag exists
        for _ in range(ratio):
            Tag.objects.create(name=fake.word(), type=random.choices(range(6), weights=[5, 0, 1, 1, 1, 1])[0])

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
            question.tags.set(random.sample(tags, min(len(tags), random.randint(0, 3))))

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
