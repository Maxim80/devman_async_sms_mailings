from quart import websocket, request
from quart_trio import QuartTrio
from dotenv import dotenv_values
from smsc_api import request_smsc
from validators import FormValidator
from exceptions import SmscApiError
import trio


app = QuartTrio(__name__)
app.config.update(dotenv_values())


async def get_page(filename):
    async with await trio.open_file(filename) as f:
        page = await f.read()

    return page


@app.route('/', methods=['GET'])
async def index():
    return await get_page(f'{app.root_path}/templates/index.html')


@app.route('/send/', methods=['POST'])
async def send():
    form = await request.form
    try:
        message = FormValidator(**form)
        smsc_resp = await request_smsc('POST', 'send',
            payload = {
                    'phones': app.config['PHONE_NUMBER'],
                    'mes': message.text,
                    'valid': 1,
            })
    except SmscApiError as e:
        return {'errorMessage': str(e)}

    return smsc_resp


# @app.websocket('/ws')
# async def ws():
#     while True:
#         await websocket.send('hello')


if __name__ == '__main__':
    app.run()
