from quart import websocket, render_template
from quart_trio import QuartTrio
from trio import open_file

app = QuartTrio(__name__)

async def get_page(filename):
    async with await open_file(filename) as f:
        page = await f.read()

    return page


@app.route('/', methods=['GET'])
async def hello():
    return await get_page(f'{app.root_path}/templates/index.html')

@app.websocket('/ws')
async def ws():
    while True:
        await websocket.send('hello')


if __name__ == '__main__':
    app.run()
