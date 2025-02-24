from django.db import models
from django.conf import settings


class Prompt(models.Model):
    """
    Модель для хранения промптов API.
    """
    MODEL_CHOICES = [model for sublist in settings.MODELS.values() for model in sublist]
    title = models.CharField(max_length=255)
    model = models.CharField(max_length=20, choices=MODEL_CHOICES, default='gpt-4o',
                             help_text="Выберите модель API")
    developer_content = models.TextField(help_text="Системное сообщение для API", blank=True, null=True)
    user_content = models.TextField(help_text="Контент от пользователя", blank=True, null=True)
    temperature = models.FloatField(default=0.0, help_text="Температура генерации (0-1)")
    max_tokens = models.PositiveIntegerField(default=1000, help_text="Максимальное количество токенов")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
