from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api import auth, gigachat, me, admin

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(gigachat.router)
app.include_router(me.router)
app.include_router(admin.router)