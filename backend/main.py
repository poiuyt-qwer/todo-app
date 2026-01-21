from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class TaskBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field()
    
class Task(TaskBase, table=True):
    is_complete: bool = Field(default=False)
    # add datetime

class TaskPublic(TaskBase):
    is_complete: bool = Field(default=False)
    
class TaskCreate(TaskBase):
    is_complete: bool = Field(default=False)
    # add datetime
    pass

class TaskUpdate(TaskBase):
    is_complete: bool | None = None
    
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args = connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
@app.post("/tasks")
def create_task(task: TaskCreate, session: SessionDep):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/tasks")
def read_tasks(session: SessionDep) -> list[Task]:
    tasks = session.exec(select(Task)).all()
    return tasks

@app.patch("/tasks/{id}")
def toggle_task_status(id: int, task: TaskUpdate, session: SessionDep):
    task_db = session.get(Task, id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)    
    return task_db

@app.put("/tasks/{id}")
def update_task(id: int, task: TaskUpdate, session: SessionDep):
    task_db = session.get(Task, id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)    
    return task_db
    
@app.delete("/tasks/{id}")
def delete_task(id: int, session: SessionDep):
    task = session.get(Task, id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}