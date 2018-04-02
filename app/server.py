from aiohttp import web
from .db import redis


async def handleGet(request):
    id = request.match_info.get('id')
    res = await redis.get_data_by_user(app, id)
    return web.json_response({
        'user': id,
        'data': res
    })


async def handlePost(request):
    try:
        data = await request.post()
    except Exception as ex:
        print(ex)
    if not data.get('id'):
        return web.json_response({
            'error': 'No id provided in post request'
        })
    if not data.get('data'):
        return web.json_response({
            'error': 'No data provided in post request'
        })
    res = await redis.save_data(app, data['id'], data['data'])
    if res:
        return web.json_response({
            'status': True
        })
    return web.json_response({
        'error': 'Error while inserting data in redis. Try again later'
    })


app = web.Application()
app.on_startup.append(redis.connect_redis)
app.on_cleanup.append(redis.close_redis)
app.add_routes([web.get('/{id}', handleGet),
                web.post('/save', handlePost)])

