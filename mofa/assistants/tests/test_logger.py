# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
from unittest import TestCase
from unittest.mock import patch

from assistants import logger


class TestLogger(TestCase):
    @patch('logging.warning')
    def test_log_response_all(self, a):
        logger.log_response(
            'dummy_url', 'dummy_status_code', params='dummy_p: dummy_p_value',
            headers='dummy_h: dummy_h_value', json='dummy_j: dummy_j_value', text='dummy_text')

        a.assert_called_with('API error! Status code = dummy_status_code. Data = dummy_url dummy_p: dummy_p_value '
                             'dummy_h: dummy_h_value dummy_j: dummy_j_value dummy_text')

    @patch('logging.warning')
    def test_log_response_none(self, a):
        logger.log_response('dummy_url', 'dummy_status_code')

        a.assert_called_with('API error! Status code = dummy_status_code. Data = dummy_url')
