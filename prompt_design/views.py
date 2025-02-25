import os
import requests
import json
import logging
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Prompt
from .forms import PromptForm
from django.conf import settings

# Настроим логирование ошибок
logger = logging.getLogger(__name__)

# Загружаем API-ключ из .env
load_dotenv()

API_KEY_OPENAI = os.getenv("API_KEY_OPENAI")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

API_KEY_GROK = os.getenv("API_KEY_GROK")
GROK_URL = "https://api.x.ai/v1/chat/completions"

API_KEY_DEEPSEEK = os.getenv("API_KEY_DEEPSEEK")
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Логиним после регистрации
            return redirect('prompt_design:prompt_list')
    else:
        form = UserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})


@login_required
def prompt_list(request):
    prompts = Prompt.objects.all().order_by('-created_at')
    return render(request, 'prompt_design/prompt_list.html', {'prompts': prompts})


@login_required
def prompt_detail(request, pk):
    prompt = get_object_or_404(Prompt, pk=pk)
    return render(request, 'prompt_design/prompt_detail.html', {'prompt': prompt})


@login_required
def prompt_create(request):
    if request.method == "POST":
        form = PromptForm(request.POST)
        if form.is_valid():
            prompt = form.save()
            return redirect('prompt_design:prompt_detail', pk=prompt.pk)
    else:
        form = PromptForm()
    return render(request, 'prompt_design/prompt_form.html', {'form': form})


@login_required
def prompt_edit(request, pk):
    prompt = get_object_or_404(Prompt, pk=pk)
    if request.method == "POST":
        form = PromptForm(request.POST, instance=prompt)
        if form.is_valid():
            form.save()
            return redirect('prompt_design:prompt_detail', pk=prompt.pk)
    else:
        form = PromptForm(instance=prompt)
    return render(request, 'prompt_design/prompt_form.html', {'form': form, 'edit_mode': True})


@login_required
def prompt_list(request):
    """Отображает список промптов."""
    prompts = Prompt.objects.all().order_by('-created_at')
    return render(request, 'prompt_design/prompt_list.html', {'prompts': prompts})


@login_required
def prompt_detail(request, pk):
    """Отображает детальную страницу промпта."""
    prompt = get_object_or_404(Prompt, pk=pk)
    return render(request, 'prompt_design/prompt_detail.html', {'prompt': prompt})


@login_required
def prompt_create(request):
    """Создает новый промпт."""
    if request.method == "POST":
        form = PromptForm(request.POST)
        if form.is_valid():
            prompt = form.save()
            return redirect('prompt_design:prompt_detail', pk=prompt.pk)
    else:
        form = PromptForm()
    return render(request, 'prompt_design/prompt_form.html', {'form': form})


@login_required
def prompt_edit(request, pk):
    """Редактирует существующий промпт."""
    prompt = get_object_or_404(Prompt, pk=pk)
    if request.method == "POST":
        form = PromptForm(request.POST, instance=prompt)
        if form.is_valid():
            form.save()
            return redirect('prompt_design:prompt_detail', pk=prompt.pk)
    else:
        form = PromptForm(instance=prompt)
    return render(request, 'prompt_design/prompt_form.html', {'form': form, 'edit_mode': True})


@login_required
@csrf_exempt
def prompt_delete(request, pk):
    """
    Удаляет промпт через AJAX-запрос.
    """
    if request.method == "POST":
        prompt = get_object_or_404(Prompt, pk=pk)
        prompt.delete()
        return JsonResponse({"status": "success", "message": "Промпт видалено."})

    return JsonResponse({"status": "error", "message": "Неправильний метод запиту."})


def detect_api(model: str) -> str:
    for key, sublist in settings.MODELS.items():
        if model in [item[0] for item in sublist]:
            return key


def clean_markdown_response(response_text):
    """
    Определяет, является ли ответ API JSON или Markdown.
    Если Markdown – удаляет ```json ... ```, иначе возвращает как есть.
    """
    response_text = response_text.strip()
    if response_text.startswith("```json") and response_text.endswith("```"):
        response_text = response_text[7:-3].strip()  # Убираем Markdown-обертку
    return response_text


def detect_response_type(response_text):
    """
    Определяет, является ли текст JSON или обычным текстом.
    """
    try:
        json_object = json.loads(response_text)  # Пробуем парсить JSON
        return json_object  # Если успешно, это JSON
    except json.JSONDecodeError:
        return response_text  # Если ошибка, это просто текст


@login_required
@csrf_exempt
def test_prompt(request):
    """
    Тестирует промпт, отправляя его в API OpenAI.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Недопустимый метод запроса"})

    if not API_KEY_OPENAI:
        return JsonResponse({"status": "error", "message": "API-ключ не найден. Проверьте файл .env"})

    try:
        title = request.POST.get("title", "Без названия")
        model = request.POST.get("model", "gpt-4o")
        developer_content = request.POST.get("developer_content", "")
        user_content = request.POST.get("user_content", "")
        drug_instruction = request.POST.get("drug_instruction", "").strip()
        temperature = float(request.POST.get("temperature", 0))
        max_tokens = int(request.POST.get("max_tokens", 1000))
        prompt_id = request.POST.get("prompt_id")

        if drug_instruction:
            user_content = user_content + f'\n\nИнструкция препарата:\n"{drug_instruction}"'

        api_type = detect_api(model)

        if api_type == 'OpenAI':
            headers = {
                "Authorization": f"Bearer {API_KEY_OPENAI}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "developer", "content": developer_content},
                    {"role": "user", "content": user_content}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            response = requests.post(OPENAI_URL, headers=headers, data=json.dumps(data))

        elif api_type == 'Grok':
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY_GROK}"
            }

            data = {
                "messages": [
                    {"role": "system", "content": developer_content},
                    {"role": "user", "content": user_content}
                ],
                "model": model,
                "stream": False,
                "temperature": 0.1
            }
            response = requests.post(GROK_URL, headers=headers, json=data)

        elif api_type == 'DeepSeek':
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY_DEEPSEEK}"
            }

            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": developer_content},
                    {"role": "user", "content": user_content}
                ]
            }

            response = requests.post(DEEPSEEK_URL, headers=headers, data=json.dumps(data))

        else:
            return JsonResponse({
                "status": "error",
                "message": f"Ошибка в имени модели '{model}', не подходит доступным API",
            })

        try:
            result = response.json()
        except json.JSONDecodeError:
            logger.error(f"Ошибка парсинга JSON от {api_type}. Ответ сервера:\n{response.text}")
            return JsonResponse({
                "status": "error",
                "message": f"Ошибка парсинга JSON от {api_type}",
                "details": response.text
            })

        if 'choices' in result and len(result['choices']) > 0:
            raw_content = result['choices'][0]['message']['content']
            cleaned_content = clean_markdown_response(raw_content)  # Убираем Markdown
            parsed_content = detect_response_type(cleaned_content)  # Определяем, JSON это или нет

            return JsonResponse({
                "status": "success",
                "response": parsed_content,  # Если JSON, передаем как объект, если текст – как строку
                "prompt_id": prompt_id
            })
        else:
            logger.error(f"Ошибка API {api_type}: {result}")
            return JsonResponse({
                "status": "error",
                "message": f"Ошибка в ответе API {api_type}",
                "details": json.dumps(result, indent=2, ensure_ascii=False)
            })

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при запросе к {api_type}: {e}")
        return JsonResponse({
            "status": "error",
            "message": f"Ошибка сети при запросе к {api_type}",
            "details": str(e)
        })

    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON от {api_type}: {e}")
        return JsonResponse({
            "status": "error",
            "message": f"Ошибка парсинга JSON от {api_type}",
            "details": str(e)
        })
