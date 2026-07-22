import factory
from factory.django import DjangoModelFactory
from apps.accounts.models import CustomUser


class UserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f"user{n}@cqsts.com")
    full_name = factory.Faker("name")
    role = "analyst"
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "TestPass123!")


class AdminFactory(UserFactory):
    role = "admin"
    is_staff = True


class QAManagerFactory(UserFactory):
    role = "qa_manager"


class SupervisorFactory(UserFactory):
    role = "supervisor"
