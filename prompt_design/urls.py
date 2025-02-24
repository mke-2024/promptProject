from django.urls import path
from .views import prompt_list, prompt_detail, prompt_create, prompt_edit, prompt_delete, test_prompt

app_name = "prompt_design"

urlpatterns = [
    path("", prompt_list, name="prompt_list"),
    path("<int:pk>/", prompt_detail, name="prompt_detail"),
    path("new/", prompt_create, name="prompt_create"),
    path("<int:pk>/edit/", prompt_edit, name="prompt_edit"),
    path("<int:pk>/delete/", prompt_delete, name="prompt_delete"),  # Удаление промпта
    path("test/", test_prompt, name="test_prompt"),  # Тестирование промпта
]
