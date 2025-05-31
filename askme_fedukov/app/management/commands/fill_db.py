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
        parser.add_argument('ratio', type=int,
                            help='The ratio of records to create')

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(
            f'Starting to fill the database with a ratio of {ratio}')

        with tqdm(total=6, desc="Filling DB", unit="step") as pbar:
            self.create_test_user()
            pbar.update(1)

            self.create_users(ratio)
            pbar.update(1)

            self.create_tags(ratio)
            pbar.update(1)

            self.create_questions(ratio)
            pbar.update(1)

            self.create_answers(ratio)
            pbar.update(1)

            self.create_likes(ratio)
            pbar.update(1)
        self.stdout.write(self.style.SUCCESS(
            f'Successfully filled the database with test data'))

    def create_test_user(self):
        test_user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'testuser@example.com',
                      'is_superuser': True, 'is_staff': True}
        )
        test_user.set_password('testpassword')
        test_user.is_superuser = True
        test_user.is_staff = True
        test_user.save()

        # Create a test profile for the test user
        Profile.objects.get_or_create(user=test_user)

    def create_users(self, ratio):
        created = 0
        attempts = 0
        max_attempts = ratio * 10
        existing_usernames = set(
            User.objects.values_list('username', flat=True))
        while created < ratio and attempts < max_attempts:
            attempts += 1
            username = fake.user_name()
            if username in existing_usernames:
                continue
            user = User.objects.create_user(
                username=username,
                email=fake.unique.email(),
                password='password',
            )
            avatar = random.choice(
                ['avatars/default.png', 'avatars/avatar1.webp', 'avatars/avatar2.jpg'])
            Profile.objects.create(user=user, avatar=avatar)
            existing_usernames.add(username)
            created += 1

    def create_tags(self, ratio):
        # See models.Tag.TAG_CHOICES
        # Make sure 'hot' tag exists
        Tag.objects.get_or_create(name='hot', type=1)
        created = 0
        attempts = 0
        max_attempts = ratio * 10
        existing_names = set(Tag.objects.values_list('name', flat=True))
        while created < ratio and attempts < max_attempts:
            attempts += 1
            name = fake.word()
            if name in existing_names:
                continue
            Tag.objects.create(name=name, type=random.choices(
                range(6), weights=[5, 0, 1, 1, 1, 1])[0])
            existing_names.add(name)
            created += 1

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
            question.tags.set(random.sample(
                tags, min(len(tags), random.randint(0, 3))))

    def create_answers(self, ratio):
        profiles = list(Profile.objects.all())
        questions = list(Question.objects.all())
        for _ in range(ratio * 100):
            Answer.objects.create(
                author=random.choice(profiles),
                question=random.choice(questions),
                content=fake.text(),
                created_at=now(),
                is_correct=random.random() < 0.1  # 1/10 chance to be correct
            )

    def create_likes(self, ratio):
        profiles = list(Profile.objects.all())
        questions = list(Question.objects.all())
        answers = list(Answer.objects.all())

        likes_added = 0
        attempts = 0
        max_attempts = ratio * 2000 * 10  # Prevent infinite loop

        while likes_added < 2000 and attempts < max_attempts:
            attempts += 1
            user = random.choice(profiles)
            if random.choice([True, False]):
                question = random.choice(questions)
                if not QuestionLike.objects.filter(user=user, question=question).exists():
                    QuestionLike.objects.create(
                        user=user,
                        question=question,
                        is_dislike=random.choice([True, True, True, False])
                    )
                    likes_added += 1
            else:
                answer = random.choice(answers)
                if not AnswerLike.objects.filter(user=user, answer=answer).exists():
                    AnswerLike.objects.create(
                        user=user,
                        answer=answer,
                        is_dislike=random.choice([True, True, False])
                    )
                    likes_added += 1
