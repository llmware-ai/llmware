from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from blockchain.api import bchain_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(bchain_router, prefix="/api")

# app.mount("/api/dwd", StaticFiles(directory="assets"), name="download")
# app.mount("/certificate", StaticFiles(directory="certificates"), name="certificates")
# app.mount("/", StaticFiles(directory="dist"), name="index.html")

uvicorn.run(app, host="localhost", port=8000)