# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""
WSGI config for mofa project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mofa.settings')

application = get_wsgi_application()
