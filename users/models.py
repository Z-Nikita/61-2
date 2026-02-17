from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Профиль пользователя (OneToOne)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    image = models.ImageField(null=True, blank=True, upload_to="profile/")
    age = models.IntegerField(default=20)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.age}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_user(sender, instance, created, **kwargs):
    """Автоматически создаём профиль при создании пользователя."""
    if created:
        Profile.objects.get_or_create(user=instance)
