from django.apps import AppConfig

class AiCourtroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'AI_courtroom'

    def ready(self):
        import AI_courtroom.signals