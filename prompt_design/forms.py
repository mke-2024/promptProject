from django import forms
from .models import Prompt


class PromptForm(forms.ModelForm):
    """
    Форма для создания и редактирования промптов.
    Добавлена валидация обязательных полей.
    """

    drug_instruction = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите текст инструкции препарата...',
            'rows': 4
        }),
        label="Инструкция препарата"
    )

    class Meta:
        model = Prompt
        fields = ['title', 'model', 'developer_content', 'user_content', 'temperature', 'max_tokens']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок', 'required': 'required'}),
            'model': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'developer_content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Системное сообщение', 'rows': 3, 'required': 'required'}),
            'user_content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Контент от пользователя', 'rows': 5, 'required': 'required'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.0', 'max': '1.0', 'required': 'required'}),
            'max_tokens': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '2000', 'required': 'required'}),
        }
        labels = {
            'title': 'Заголовок',
            'model': 'Модель',
            'developer_content': 'Системное сообщение (developer role)',
            'user_content': 'Контент от пользователя (user role)',
            'temperature': 'Temperature (0-1)',
            'max_tokens': 'Max Tokens (1-2000)',
        }

    def clean(self):
        """
        Дополнительная валидация формы.
        """
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        developer_content = cleaned_data.get("developer_content")
        user_content = cleaned_data.get("user_content")

        if not title or not developer_content or not user_content:
            raise forms.ValidationError("Все обязательные поля должны быть заполнены!")

        return cleaned_data
