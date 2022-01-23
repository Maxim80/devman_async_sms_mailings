from dotenv import load_dotenv
import asyncclick as click
import os
import asks
import trio


load_dotenv()


@click.command()
@click.option('--login', default=os.getenv('SMSC_LOGIN'), help='SMSC login')
@click.option('--psw', default=os.getenv('SMSC_PASSW'), help='SMSC password')
@click.option('--phones', help='List of phone numbers entered separated by commas or semicolons')
@click.option('--mes', help='SMS message text')
@click.option('--valid', default=1, help='Undelivered SMS lifetime in hours')
async def main(**kwargs) -> None:
    send_url = 'https://smsc.ru/sys/{}.php'.format('send')
    send_params = {
        'login': kwargs['login'],
        'psw': kwargs['psw'],
        'phones': kwargs['phones'],
        'mes': kwargs['mes'],
        'valid': kwargs['valid'],
        'fmt': 3,
    }
    send = await asks.get(send_url, params=send_params)

    message_id = send.json()['id']

    status_url = 'https://smsc.ru/sys/{}.php'.format('status')
    status_params = {
        'login': kwargs['login'],
        'psw': kwargs['psw'],
        'phone': kwargs['phones'],
        'id': message_id,
        'fmt': 3,
    }
    status = await asks.get(status_url, params=status_params)
    print(status.json())


if __name__ == '__main__':
    main(_anyio_backend="trio")
