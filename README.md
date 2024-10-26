# Test task for Python Developer (Jun/Mid) - Starnavi
- [Video presentation](youtube.com)

# How to run project
- [Download Ollama](https://ollama.com/download)
- Download Gemma2 model by runnig command in cmd: __ollama run gemma2:2b__
- pip install -r requirements.txt
- First terminal: run __python manage.py runserver__
- Second terminal: run __celery -A django_moderation_project.celery worker --pool=solo -l INFO__
