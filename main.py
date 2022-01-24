from dotenv import load_dotenv
from contextvars import ContextVar
from typing import Optional
import asyncclick as click
import os
import asks
import trio


load_dotenv()

smsc_login: ContextVar[str] = ContextVar('smsc_login')
smsc_password: ContextVar[str] = ContextVar('smsc_password')
smsc_login.set(os.getenv('SMSC_LOGIN'))
smsc_password.set(os.getenv('SMSC_PASSW'))


class SmscApiError(Exception):
    pass


@click.command()
@click.option('--login', default=None, help='SMSC login')
@click.option('--psw', default=None, help='SMSC password')
@click.option('--phones', help='List of phone numbers entered separated by commas or semicolons')
@click.option('--message', help='SMS message text')
@click.option('--valid', default=1, help='Undelivered SMS lifetime in hours')
async def main(**kwargs) -> None:
    pass


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
    if http_method != 'POST' and http_method != 'GET':
        raise SmscApiError('Not the correct "http_method". Method must be "POST" or "GET"')

    if api_method != 'send' and api_method != 'status':
        raise SmscApiError('Not the correct "api_method". Method must be "send" or "status"')

    base_url = 'https://smsc.ru/sys/{}.php'

    login = login or smsc_login.get()
    password = password or smsc_password.get()

    funcs = {
        'POST': asks.post,
        'GET':asks.get,
    }

    params = {
        'login': login,
        'psw': password,
        'fmt': 3,
    }
    params.update(payload)

    response = await funcs[http_method](
        base_url.format(api_method),
        params=params,
    )

    response = response.json()
    if response.get('error'):
        raise SmscApiError(response['error'])

    return response.json()


if __name__ == '__main__':
    main(_anyio_backend="trio")
