from quart import websocket, request
from quart_trio import QuartTrio
from dotenv import dotenv_values
from smsc_api import request_smsc
from validators import FormValidator
from exceptions import SmscApiError
from sms_sending_db.db import Database
from hypercorn.trio import serve
from hypercorn.config import Config as HyperConfig
import trio_asyncio
import trio
import aioredis


app = QuartTrio(__name__)
app.config.update(dotenv_values())


async def get_page(filename):
    async with await trio.open_file(filename) as f:
        page = await f.read()

    return page


@app.before_serving
async def open_connect_to_redis():
    redis_uri = app.config['REDIS_URI']
    redis_rassword = app.config['REDIS_PASSW']
    app.redis = await aioredis.from_url(
        f'redis://{redis_uri}', password=redis_rassword)
    app.db = Database(app.redis)


@app.after_serving
async def close_connect_to_redis():
    await trio_asyncio.aio_as_trio(redis.close())


@app.route('/', methods=['GET'])
async def index():
    return await get_page(f'{app.root_path}/templates/index.html')


@app.route('/send/', methods=['POST'])
async def send():
    form = await request.form
    try:
        message = FormValidator(**form)
        sms_status = await request_smsc('POST', 'send',
            payload = {
                    'phones': app.config['PHONE_NUMBERS'],
                    'mes': message.text,
                    'valid': 1,
            })
    except SmscApiError as e:
        return {'errorMessage': str(e)}

    await trio_asyncio.aio_as_trio(app.db.add_sms_mailing(
            sms_status['id'], app.config['PHONE_NUMBERS'], message.text)
        )
    return sms_status


@app.websocket('/ws')
async def ws():
    data = {
          "msgType": "SMSMailingStatus",
          "SMSMailings": [
            {
              "timestamp": 1123131392.734,
              "SMSText": "Сегодня гроза! Будьте осторожны!",
              "mailingId": "1",
              "totalSMSAmount": 345,
              "deliveredSMSAmount": 47,
              "failedSMSAmount": 5,
            },
            {
              "timestamp": 1323141112.924422,
              "SMSText": "Новогодняя акция!!! Приходи в магазин и получи скидку!!!",
              "mailingId": "new-year",
              "totalSMSAmount": 3993,
              "deliveredSMSAmount": 801,
              "failedSMSAmount": 0,
            },
          ]
    }
    while True:
        # data = await websocket.receive()
        await websocket.send_json(data)
        for sms_mailing in data['SMSMailings']:
            sms_mailing['deliveredSMSAmount'] += 10
        await trio.sleep(1)


async def run_server():
    async with trio_asyncio.open_loop():
        config = HyperConfig()
        config.bind = [f"127.0.0.1:5000"]
        config.use_reloader = True
        await serve(app, config)


if __name__ == '__main__':
    trio.run(run_server)
