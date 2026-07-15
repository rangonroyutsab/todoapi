import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from tasks.models import Task

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.LazyFunction(lambda: make_password("securepassword123"))


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    description = "Test description"
    owner = factory.SubFactory(UserFactory)
    status = "pending"
