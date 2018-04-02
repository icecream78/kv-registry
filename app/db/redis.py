import aioredis
import asyncio


async def connect_redis(app):
    conn = await aioredis.create_redis_pool(
        'redis://localhost',
        minsize=5,
        maxsize=10
    )
    app['db'] = conn


async def close_redis(app):
    app['db'].close()
    await app['db'].wait_closed()


async def save_data(app, id, data):
    list_data = await app['db'].get(id, encoding='utf-8')
    data_index = 1
    if list_data is None:
        await app['db'].set(id, 1)  # add new key to data binding
    else:
        data_index = int(list_data.split()[-1]) + 1
        await app['db'].append(id, ' {}'.format(data_index))  # add new index to user data list

    return await app['db'].set('{}:{}'.format(id, data_index), data)  # add new data to redis


async def get_data_by_user(app, user):
    list_index = await app['db'].get(user, encoding='utf-8')
    if not list_index:
        raise Exception('No such user')

    records = list_index.split()
    futures = (app['db'].get('{}:{}'.format(user, x), encoding='utf-8') for x in records)
    res = await asyncio.gather(*futures)
    result, delete_req = [], []
    for i, data in enumerate(res):
        if data:
            delete_req.append(str(records[i]))
            result.append(data)
    # delete_req = [str(records[i]) for i,x in enumerate(res) if x]
    d = await app['db'].set(user, ' '.join(delete_req))
    return result
