# Yatube

Yatube – социальная сеть мини-блогов с возможностью добавления, редактирования, удаления постов. Реализована подписка/отписка на автора, можно добавлять авторов в избранное. Проект покрыт тестами для проверки работоспособности.

## Запуск проекта:
- Клонировать репозиторий:
```
git@github.com:apisland/hw05_final.git
```
- Создать виртуальное окружение:
```
python -m venv env или python3 -m venv env
```
```
source env/Scripts/activate или . env/bin/activate
```
- установить зависимости из файла **requirements.txt**:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
- Выполнить миграции:

```
python3 manage.py migrate или python manage.py migrate
```
- Запустить проект:

```
python3 manage.py runserver или python manage.py runserver
```
![](https://img.shields.io/badge/Python-3.7-blue)
![](https://img.shields.io/badge/Django-2.2.16-blue)
