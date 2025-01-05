from sanic import Sanic, Request, response
from utils.models import Task
from tortoise import Tortoise, run_async
from redis import ayncio as aioredis
import json

app = Sanic(__name__)
tasks = []
task_counter = 1


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



async def connect_to_db():
    await Tortoise.init(
        db_url='mysql://root:uknowwhoiam@localhost:3306/task_manager',
        modules={"models": ["utils.models"]}, 
    )    
    await Tortoise.generate_schemas()


redis_client = None

async def connect_to_redis(app, loop):
    global redis_client
    redis_client = await aioredis.create_redis_pool('redis://localhost', encoding='utf-8', loop=loop)
    app.redis = redis_client
    print("Redis connection successful")


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
async def get_task(request: Request, id: int):
    task_key = f"task:{id}"
    cached_task = await redis_client.get(task_key)
    
    if cached_task:
        print(f"Cache found for Task {id}")
        task = json.loads(cached_task)
        return response.json(task)

    task = await Task.get_or_none(id=id)
    if task:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        }
        await redis_client.set(task_key, json.dumps(task_dict), ex=300)  # Cache for 5 mins
        print(f"Cache not found for Task {id}, saved to Redis")
        return response.json(task_dict)

    return response.json({f"Task {id} not found."}, status=404)

@app.put("/tasks/<id:int>")
async def update_task(request: Request, id: int):
    task = await Task.get_or_none(id=id)
    if task:
        task.title = request.json.get("title", task.title)
        task.description = request.json.get("description", task.description)
        task.status = request.json.get("status", task.status)
        await task.save()
        task_key = f"task:{id}"
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status
        }
        await redis_client.set(task_key, json.dumps(task_dict), ex=300)
        print(f"Updated Task {id} in cache")
        return response.json({f"Task {id} updated"})

    return response.json({f"Task {id} not found."}, status=404)


@app.delete("/tasks/<id:int>")
async def delete_task(request: Request, id: int):
    task = await Task.get_or_none(id=id)
    if task:
        await task.delete()
        task_key = f"task:{id}"
        await redis_client.delete(task_key)
        print(f"Task {id} removed from cache")
        return response.json({f"Task {id} deleted"})
    
    return response.json({f"Task {id} not found."}, status=404)


if __name__ == '__main__':
    run_async(connect_to_db())
    run_async(connect_to_redis(app, app.loop))
    app.run(port = 9999, debug = True)
