# Prompt Debugger Project

Этот проект на Django предназначен для отладки промптов.

✅ проект будет работать на 185.174.220.122:8089

## Установка
1. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv venv
   source venv/bin/activate  # для Linux/MacOS
   venv\Scripts\activate     # для Windows
   
2. Установите зависимости:
```shell
pip install -r requirements.txt
``` 
3. Примените миграции:
```shell
python manage.py migrate
``` 
4. Запустите сервер:
```shell
python manage.py runserver
``` 
-------

### ✅ **1. Добавление пользователей через Django Admin (Самый удобный способ)**
Django уже имеет встроенную админ-панель, где можно **добавлять, удалять и редактировать пользователей**.

#### **1️⃣ Открываем Django Admin**
1. Запускаем сервер:
   ```bash
   python manage.py runserver
   ```
2. Заходим в браузере:  
   **http://127.0.0.1:8000/admin/**
3. Вводим **логин и пароль суперпользователя** (если его нет, смотри ниже 👇).
4. Переходим в раздел **"Users"** → **"Добавить пользователя"**.
5. Заполняем данные:  
   - **Имя пользователя**  
   - **Email (по желанию)**  
   - **Пароль**  
   - **Выбираем статус "Активный"**
6. Нажимаем **"Сохранить"**.  

✅ **Теперь пользователь создан и может войти через `/login/`.**


# Инициализация Git-репозитория и загрузка на GitHub

```bash
echo "# promptProject" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:mke-2024/promptProject.git
git push -u origin main

✅ **Шаги:**
1. **Создаем `README.md`** и записываем в него заголовок `promptProject`.
2. **Инициализируем Git-репозиторий** в текущей папке.
3. **Добавляем `README.md` в индекс Git** (`git add`).
4. **Фиксируем первый коммит** (`git commit`).
5. **Переименовываем главную ветку в `main`** (`git branch -M main`).
6. **Добавляем удаленный репозиторий GitHub** (`git remote add origin`).
7. **Отправляем код в удаленный репозиторий** (`git push -u origin main`).

🚀 **Теперь проект загружен в GitHub!**
