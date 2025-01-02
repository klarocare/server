from fastapi import FastAPI
from routes import chat_api, care_task_api


app = FastAPI(root_path="/api")

app.include_router(chat_api.router)
app.include_router(care_task_api.router)


@app.get("/health-check")
async def root():
    return {"message": "ok"}
