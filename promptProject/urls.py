from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

from prompt_design.views import register


# Функция для выхода через POST
@csrf_exempt
def custom_logout(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")
    return HttpResponseRedirect("home")  # Перенаправляем на home если не POST


# Функция главной страницы
def home(request):
    if request.user.is_authenticated:
        return redirect('prompt_design:prompt_list')  # Если вошел, ведем на список промптов
    return render(request, 'home.html')  # Гостям показываем страницу входа


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('prompts/', include(('prompt_design.urls', 'prompt_design'), namespace='prompt_design')),

    # Вход / выход / регистрация
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),  # Теперь выход работает через POST
]
