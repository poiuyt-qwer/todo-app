from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field()
    is_complete: bool = Field(default=False)
    
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
def create_task(task: Task, session: SessionDep) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks")
def read_tasks(session: SessionDep) -> list[Task]:
    tasks = session.exec(select(Task)).all()
    return tasks