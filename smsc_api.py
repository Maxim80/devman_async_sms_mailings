from dotenv import load_dotenv
from contextvars import ContextVar
from typing import Optional
from unittest.mock import patch, Mock
from exceptions import SmscApiError
import asyncclick as click
import os
import asks
import trio


load_dotenv()

smsc_login: ContextVar[str] = ContextVar('smsc_login')
smsc_password: ContextVar[str] = ContextVar('smsc_password')
smsc_login.set(os.getenv('SMSC_LOGIN'))
smsc_password.set(os.getenv('SMSC_PASSW'))


@click.command()
@click.option('--login', default=None, help='SMSC login')
@click.option('--psw', default=None, help='SMSC password')
@click.option('--phones', help='List of phone numbers entered separated by commas or semicolons')
@click.option('--message', help='SMS message text')
@click.option('--valid', default=1, help='Undelivered SMS lifetime in hours')
async def main(**kwargs) -> None:
    response = await request_smsc(
            'POST',
            'send',
            payload={
                'phones': kwargs['phones'],
                'mes': kwargs['message'],
                'valid': kwargs['valid'],
            }
        )
    print(response)

    message_id = response['id']
    message_status = await request_smsc(
            'GET',
            'status',
            payload={
                'phone': kwargs['phones'],
                'id': message_id
            }
        )
    print(message_status)


async def substitute_asks_post(*args, **kwargs):
    response = Mock()
    response.json.return_value = {'id': 22, 'cnt': 1}
    return response


@patch('asks.post', substitute_asks_post)
async def request_smsc(
        http_method: str,
        api_method: str,
        login: Optional[str]=None,
        password: Optional[str]=None,
        payload: dict = {}
    ) -> dict:
    """Send request to SMSC.ru service.

    Args:
        http_method (str): E.g. 'GET' or 'POST'.
        api_method (str): E.g. 'send' or 'status'.
        login (str): Login for account on smsc.ru.
        password (str): Password for account on smsc.ru.
        payload (dict): Additional request params, override default ones.
    Returns:
        dict: Response from smsc.ru API.
    Raises:
        SmscApiError: If smsc.ru API response status is not 200 or JSON response
        has "error_code" inside.

    Examples:
        >>> await request_smsc(
        ...   'POST',
        ...   'send',
        ...   login='smsc_login',
        ...   password='smsc_password',
        ...   payload={'phones': '+79123456789'}
        ... )
        {'cnt': 1, 'id': 24}
        >>> await request_smsc(
        ...   'GET',
        ...   'status',
        ...   login='smsc_login',
        ...   password='smsc_password',
        ...   payload={
        ...     'phone': '+79123456789',
        ...     'id': '24',
        ...   }
        ... )
        {'status': 1, 'last_date': '28.12.2019 19:20:22', 'last_timestamp': 1577550022}
    """
    if http_method not in {'POST', 'GET'}:
        raise SmscApiError('Not the correct "http_method". Method must be "POST" or "GET".')

    if api_method not in {'send', 'status'}:
        raise SmscApiError('Not the correct "api_method". Method must be "send" or "status".')

    login = login or smsc_login.get()
    password = password or smsc_password.get()

    funcs = {
        'POST': asks.post,
        'GET':asks.get,
    }

    url = f'https://smsc.ru/sys/{api_method}.php'
    params = {
        'login': login,
        'psw': password,
        'fmt': 3,
        'charset': 'utf-8',
        **payload
    }

    response = await funcs[http_method](url, params=params)
    response = response.json()

    if response.get('error'):
        raise SmscApiError(response['error'])

    return response


if __name__ == '__main__':
    main(_anyio_backend="trio")
