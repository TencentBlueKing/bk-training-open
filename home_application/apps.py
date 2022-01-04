from django.apps import AppConfig
from django.db.models.signals import post_migrate


def init_super(signal, **kwargs):
    from django.conf import settings

    from blueapps.account import get_user_model

    user_model = get_user_model()
    user_model.objects.filter(username__in=settings.INIT_SUPERUSER).update(is_superuser=True, is_staff=True)


class HomeApplicationConfig(AppConfig):
    name = "home_application"
    verbose_name = "主应用"

    def ready(self):
        post_migrate.connect(init_super, sender=self)
