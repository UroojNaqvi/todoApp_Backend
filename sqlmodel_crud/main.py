from contextlib import asynccontextmanager
from http.client import HTTPException
from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(index=True)


sqlite_url = f"postgresql://UroojNaqvi:t2GcU4pNqlur@ep-tight-leaf-88437295.us-east-2.aws.neon.tech/neondb?sslmode=require"


engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def task_exists(session: Session, content: str) -> bool:
    statement = select(Task).where(Task.content == content)
    result = session.exec(statement)
    return bool(result.first())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    create_db_and_tables()
    yield


app: FastAPI = FastAPI(lifespan=lifespan)


@app.post("/task/")
def create_task(task: Task):
    with Session(engine) as session:
        if task_exists(session, task.content):
            raise HTTPException(status_code=400, detail="Task already exists")
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.put("/task/")
def update_task(task: Task):
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task.id)
        results = session.exec(statement)
        db_task = results.one()

        db_task.content = task.content
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task


@app.get("/task/")
def read_task():
    with Session(engine) as session:
        task = session.exec(select(Task)).all()
        return task


@app.delete("/task/")
def delete_task(task: Task):
    with Session(engine) as session:
        statement = select(Task).where(Task.id == task.id)
        results = session.exec(statement)
        db_task = results.one()

        session.delete(db_task)
        session.commit()
        return "task deleted...."
