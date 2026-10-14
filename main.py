from contextlib import closing
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Task Manager API", version="1.0.0")
DB = "tasks.db"
def connect():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row; return con
with closing(connect()) as con:
    con.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', completed INTEGER NOT NULL DEFAULT 0)")
    con.commit()
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool | None = None
def out(row):
    d=dict(row); d['completed']=bool(d['completed']); return d
@app.get('/')
def root(): return {"message":"Task Manager API", "docs":"/docs", "health":"/health"}
@app.get('/health')
def health(): return {"status":"ok"}
@app.get('/tasks')
def list_tasks():
    with closing(connect()) as con: rows=con.execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()
    return [out(r) for r in rows]
@app.post('/tasks', status_code=201)
def create_task(task: TaskCreate):
    with closing(connect()) as con:
        cur=con.execute('INSERT INTO tasks(title,description) VALUES (?,?)',(task.title.strip(),task.description.strip())); con.commit()
        row=con.execute('SELECT * FROM tasks WHERE id=?',(cur.lastrowid,)).fetchone()
    return out(row)
@app.patch('/tasks/{task_id}')
def update_task(task_id: int, update: TaskUpdate):
    changes=update.model_dump(exclude_unset=True)
    if not changes: raise HTTPException(400,'Provide at least one field to update')
    if 'completed' in changes and changes['completed'] is not None: changes['completed']=int(changes['completed'])
    allowed={'title','description','completed'}
    if not set(changes).issubset(allowed): raise HTTPException(400,'Invalid field')
    with closing(connect()) as con:
        if con.execute('SELECT id FROM tasks WHERE id=?',(task_id,)).fetchone() is None: raise HTTPException(404,'Task not found')
        for key,value in changes.items():
            if value is not None: con.execute(f'UPDATE tasks SET {key}=? WHERE id=?',(value,task_id))
        con.commit(); row=con.execute('SELECT * FROM tasks WHERE id=?',(task_id,)).fetchone()
    return out(row)
@app.delete('/tasks/{task_id}', status_code=204)
def delete_task(task_id: int):
    with closing(connect()) as con:
        cur=con.execute('DELETE FROM tasks WHERE id=?',(task_id,)); con.commit()
        if cur.rowcount==0: raise HTTPException(404,'Task not found')
