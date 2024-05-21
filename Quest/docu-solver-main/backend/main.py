from fastapi import FastAPI
from api.ask import router as ask_router
from api.upload import router as upload_router
from middlewares.log_requests import LogRequestsMiddleware
from config.settings import add_cors_middleware

app = FastAPI()

# Add CORS middleware
add_cors_middleware(app)

# Add custom logging middleware
app.add_middleware(LogRequestsMiddleware)

# Include routers
app.include_router(ask_router, prefix="/api", tags=["ask"])
app.include_router(upload_router, prefix="/api", tags=["upload"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
