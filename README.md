# Test task for Python Developer (Jun/Mid) - Starnavi
- [Video presentation](https://youtu.be/ZZBmYYKMjaw)

# How to run project
1. [Download Ollama](https://ollama.com/download)
2. Download Gemma2 model by running command in cmd: __ollama run gemma2:2b__
3. pip install -r requirements.txt
4. First terminal: __python manage.py runserver__
5. Second terminal: __celery -A django_moderation_project.celery worker --pool=solo -l INFO__
