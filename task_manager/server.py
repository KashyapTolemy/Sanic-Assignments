from sanic import Sanic, Request, response
from utils.models import Task
from tortoise import Tortoise
import redis.asyncio as redis
import json


app = Sanic(__name__)


TORTOISE_CONNECT = {
    "connections": {
        "default": "mysql://root:uknowwhoiam@localhost:3306/task_manager"
    },
    "apps": {
        "models": {
            "models": ["utils.models"],
            "default_connection": "default",
        }
    }
}


async def connect_to_db(app,loop):
    await Tortoise.init(
        db_url='mysql://root:uknowwhoiam@localhost:3306/task_manager',
        modules={"models": ["utils.models"]}, 
    )    
    await Tortoise.generate_schemas()


@app.post("/tasks")
async def create_task(request: Request):
    task = await Task.create(
        title = request.json.get('title'),
        description = request.json.get('description'),
        status = request.json.get('status','pending')
        )
    return response.json(f"Task {task.id} : {task.title} Created.")


@app.get("/tasks")
async def get_all_tasks(request: Request):
    tasks = await Task.all()
    return response.json(f"{tasks}\n\n All Tasks received.")


@app.get("/tasks/<id:int>")
async def get_task(request: Request,id):
    cache_key = f"task:{id}"
    cached_task = await app.ctx.redis.get(cache_key)

    if cached_task:
        return response.json(json.loads(cached_task), status=200)
    else:
        task = await Task.get(id = id)

        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        }

        await app.ctx.redis.setex(cache_key, 300, json.dumps(task_data))

        return response.json(f"{task_data}", status=200)


@app.put("tasks/<id:int>")
async def update_task(request: Request,id):
    task = await Task.get(id=id)
    
    if task is None:
        return response.json(f"Task {id} not found.", status=404)

    task.title = request.json.get('title', task.title)
    task.description = request.json.get('description', task.description)
    task.status = request.json.get('status', task.status)
    
    await task.save()

    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status
    }

    cache_key = f"task:{id}"
    await app.ctx.redis.setex(cache_key, 300, json.dumps(task_data))

    return response.json(task_data, status=200)


@app.delete("tasks/<id:int>")
async def delete_task(request: Request,id):
    task = await Task.get(id=id)

    if task is None:
        return response.json(f"Task {id} not found.", status=404)

    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status
    }

    await task.delete()

    cache_key = f"task:{id}"
    await app.ctx.redis.delete(cache_key)

    return response.json(f"Task {id} deleted., task: {task_data}", status=200)


@app.before_server_start
async def setup_db(app, loop):
    await connect_to_db(app, loop)


@app.before_server_start
async def connect_to_redis(app):
    app.ctx.redis = redis.Redis(
        host='localhost', 
        port=6379, 
        db=0, 
        decode_responses=True
    )
    
    await app.ctx.redis.ping()


@app.after_server_stop
async def close_redis(app,loop):
    await app.ctx.redix.close()


if __name__ == '__main__':
    app.run(port = 9999, debug = True)
