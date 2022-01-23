from dotenv import load_dotenv
import asyncclick as click
import os
import asks
import trio


def get_params(login: str, psw: str, phones: str,
               message: str, valid: int) -> dict:
    return {
        'login': login,
        'psw': psw,
        'phones': phones.strip(' ;,'),
        'mes': message,
        'valid': valid,
    }


async def get_request(url: str, params: dict) -> asks.response_objects.Response:
    request = await asks.get(url, params=params)
    return request


load_dotenv()


@click.command()
@click.option('--login', default=os.getenv('SMSC_LOGIN'), help='SMSC login')
@click.option('--psw', default=os.getenv('SMSC_PASSW'), help='SMSC password')
@click.option('--phones', help='List of phone numbers entered separated by commas or semicolons')
@click.option('--mes', help='SMS message text')
@click.option('--valid', default=1, help='Undelivered SMS lifetime in hours')
async def main(**kwargs) -> None:
    base_url = 'https://smsc.ru/sys/send.php'
    params = get_params(kwargs['login'], kwargs['psw'], kwargs['phones'],
                        kwargs['mes'], kwargs['valid'])
    request = await get_request(base_url, params)


if __name__ == '__main__':
    main(_anyio_backend="trio")
