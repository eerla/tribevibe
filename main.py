from fastapi import FastAPI
from routers import users, events, groups
from fastapi.middleware.cors import CORSMiddleware

#url = http://127.0.0.1:8000/docs#/default/login_login_post
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend's address for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router)
app.include_router(events.router)
app.include_router(groups.router)

@app.get("/")
def root():
    return {"message": "Tribe Vibe - Authentication"}
