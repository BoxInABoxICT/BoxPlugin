# This program has been developed by students from the bachelor Computer Science at Utrecht University within the
# Software and Game project course
# ©Copyright Utrecht University Department of Information and Computing Sciences.
"""This file contains the logger."""
import logging


def log_response(url, status_code, params=None, headers=None, data=None, json=None, text=None):
    """
    Log a response.

    :param status_code: Status code of the response.
    :type status_code: int
    :param data: Data of the response.
    :type data: dict
    :param url: The URL the request was sent to.
    :type url: str
    :param params: The parameters used for the request.
    :type params: dict
    :param headers: The headers used for the request.
    :type headers: dict(str,str)
    :param json: The json used for the request.
    :type json: dict
    :param text: The response text to log.
    :type text: str
    """
    ret = [f'API error! Status code = {status_code}. Data = {url}']

    if params is not None:
        ret.append(f'{params}')
    if headers is not None:
        ret.append(f'{headers}')
    if data is not None:
        ret.append(f'{data}')
    if json is not None:
        ret.append(f'{json}')
    if text is not None:
        ret.append(text.replace('\n', ''))

    logging.warning(' '.join(ret))


def log_text(text):
    """
    Put text in logger.

    :param text: The text for the logger.
    :type text: str
    """
    logging.warning(text)


def log_assistants(message, assistant_name):
    """
    Log an assistant information message.

    :param message: The message to be logged
    :type message: str
    :param assistant_name: The name of the assistant
    :type assistant_name: str
    """
    logging.warning(f'{assistant_name}: {message}')
