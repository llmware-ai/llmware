from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from global_vars import Var
from database import FamAIDataBase
from contextlib import asynccontextmanager


# ON STARTUP FUNCTION
@asynccontextmanager
async def lifespan(_fastapi: FastAPI):
    Var.db = FamAIDataBase()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
