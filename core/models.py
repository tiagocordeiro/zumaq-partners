import uuid

from django.contrib.auth.models import User
from django.db import models


def make_secret():
    return str(uuid.uuid4())


class TimeStampedModel(models.Model):
    created = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
    )
    modified = models.DateTimeField(
        'modificado em',
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        abstract = True


class Active(models.Model):
    active = models.BooleanField('ativo', default=True)

    class Meta:
        abstract = True


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profiles/')
    api_view = models.BooleanField("Habilitar API programática", default=False)
    api_secret_key = models.CharField(max_length=36, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Profiles"

    def save(self, *args, **kwargs):
        if self.api_secret_key is None:
            self.api_secret_key = make_secret()
        super(UserProfile, self).save(*args, **kwargs)


class CotacoesMoedas(models.Model):
    date = models.DateField(primary_key=True)
    usd = models.DecimalField(decimal_places=2, max_digits=20, blank=True, null=True)
    cny = models.DecimalField(decimal_places=2, max_digits=20, blank=True, null=True)
