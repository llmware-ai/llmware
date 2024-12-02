from fastapi.middleware.cors import CORSMiddleware

def add_cors(app):
    # List of allowed origins (can be '*' to allow all origins)
    allowed_origins = [
        "*"  # Add any other domain you want to allow
    ]

    # Adding CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Specifies allowed origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
        allow_headers=["*"],  # Allow all headers
    )