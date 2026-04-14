from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth, gigachat, me, admin
from services.auth_init import ensure_default_admin  # <- импорт инициализатора

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# создаём дефолтного админа при старте, если пользователей (или админов) ещё нет
@app.on_event("startup")
def startup_event():
   # ensure_default_admin()
    pass

app.include_router(auth.router)
app.include_router(gigachat.router)
app.include_router(me.router)
app.include_router(admin.router)