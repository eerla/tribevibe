from fastapi import FastAPI
from routers import users
#url = http://127.0.0.1:8000/docs#/default/login_login_post
app = FastAPI()

app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Meetup Clone API - Authentication"}
