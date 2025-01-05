from sanic import Sanic, Request, response

app = Sanic(__name__)
tasks = []
task_counter = 1

@app.post("/tasks")
async def create_task(request: Request):
    global task_counter
    task= {
        "id": task_counter,
        "title": request.json.get("title"),
        "description": request.json.get("description"),
        "status": request.json.get("status","pending")
    }
    task_counter += 1
    tasks.append(task)
    return response.json(f"Task {task['id']} : {task['title']} Created.")

@app.get("/tasks")
async def get_all_tasks(request: Request):
    return response.json(f"{tasks}\n\n All Tasks received.")

@app.get("/tasks/<id>")
async def get_task(request: Request,id):
    task = None
    for t in tasks:
        if str(t['id']) == str(id):
            task = t
            break
    if task is None:
        return response.json(f"Task {id} not found.",status = 404)
    return response.json(task)

@app.put("tasks/<id>")
async def update_task(request: Request,id):
    task = None
    for t in tasks:
        if str(t['id']) == str(id):
            task = t
            break
    if task is None:
        return response.json(f"Task {id} not found.",status = 404)
    task['title'] = request.json.get('title',task['title'])
    task['description'] = request.json.get('description',task['description'])
    task['status'] = request.json.get('status',task['status'])
    return response.json(f"Task {id} updated.\n{tasks}")

@app.delete("tasks/<id>")
async def delete_task(request: Request,id):
    task = None
    for t in tasks:
        if str(t['id']) == str(id):
            task = t
            break
    if task is None:
        return response.json(f"Task {id} not found.",status = 404)
    tasks.remove(task)
    return response.json(f"Task {id} deleted.")

if __name__ == '__main__':
    app.run(port = 9999, debug = True)
