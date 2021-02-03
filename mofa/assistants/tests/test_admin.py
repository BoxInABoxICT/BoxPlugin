# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from unittest.mock import MagicMock, patch

from django.test import TestCase

from assistants.admin import AssistantAdmin


class TestAssistantAdmin(TestCase):

    @patch('assistants.learning_locker.check_statement_forwarder', return_value=True)
    def test_has_error_with_object(self, a):
        m = MagicMock()
        m.forwarder_id = "1"
        self.assertEqual(AssistantAdmin.has_error(m), False)

    @patch('assistants.learning_locker.check_statement_forwarder', return_value=False)
    def test_has_error_with_object_false(self, a):
        m = MagicMock()
        m.forwarder_id = "1"
        self.assertEqual(AssistantAdmin.has_error(m), True)

    def test_has_error_with_none_object(self):
        m = None
        self.assertEqual(AssistantAdmin.has_error(m), False)
