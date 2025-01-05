from sanic import Sanic, Request, response
from utils.models import Task
from tortoise import Tortoise, run_async

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


# @app.get("/tasks/<id>")
# async def get_task(request: Request,id):
#     task = None
#     for t in tasks:
#         if str(t['id']) == str(id):
#             task = t
#             break
#     if task is None:
#         return response.json(f"Task {id} not found.",status = 404)
#     return response.json(task)


# @app.put("tasks/<id>")
# async def update_task(request: Request,id):
#     task = None
#     for t in tasks:
#         if str(t['id']) == str(id):
#             task = t
#             break
#     if task is None:
#         return response.json(f"Task {id} not found.",status = 404)
#     task['title'] = request.json.get('title',task['title'])
#     task['description'] = request.json.get('description',task['description'])
#     task['status'] = request.json.get('status',task['status'])
#     return response.json(f"Task {id} updated.\n{tasks}")


# @app.delete("tasks/<id>")
# async def delete_task(request: Request,id):
#     task = None
#     for t in tasks:
#         if str(t['id']) == str(id):
#             task = t
#             break
#     if task is None:
#         return response.json(f"Task {id} not found.",status = 404)
#     tasks.remove(task)
#     return response.json(f"Task {id} deleted.")


if __name__ == '__main__':
    run_async(connect_to_db())
    app.run(port = 9999, debug = True)
