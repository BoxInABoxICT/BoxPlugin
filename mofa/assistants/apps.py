# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""Perform sync_agent presence check on starting the app."""
from django.apps import AppConfig
from django.conf import settings
import os
import requests


class AssistantsConfig(AppConfig):
    """Perform sync_agent presence check on starting the app."""

    name = 'assistants'

    def ready(self):
        """Perform sync agent checks, updates and creations when the server is started."""
        if os.environ.get('RUN_MAIN'):
            from assistants import sync_agent
            import django.core.validators as validators
            from django.core.exceptions import ValidationError

            validator = validators.URLValidator(schemes=("http", "https"))
            try:
                validator(os.getenv("MOODLE_BASE_URL"))
                validator(os.getenv("MOODLE_BASE_IP"))
                validator(os.getenv("MOODLE_WEBSERVICE_URL"))
                validator(os.getenv("LL_URL"))
            except ValueError:
                raise ValidationError()

            try:
                sync_agent.build_sync_agents()
            except requests.ConnectionError:
                print(f'Connection to Learning Locker was refused! Is it running on {settings.LL_URL} and reachable?')
                quit()
