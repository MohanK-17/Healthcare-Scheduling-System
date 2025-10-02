from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import admin  # Import your admin router (and any other routers)

app = FastAPI(title="Healthcare Management System API")

# ✅ CORS Setup: Allow React frontend to talk to FastAPI backend
origins = [
    "http://localhost:5173",   # React dev server
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # or ["*"] for all domains (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],        # Allow all headers
)

# ✅ Include your routers
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Root route
@app.get("/")
def root():
    return {"message": "Welcome to the Healthcare Management System API!"}

# Optional: List all available routes
@app.get("/routes")
def list_routes():
    route_list = []
    for route in app.routes:
        route_list.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods)
        })
    return {"routes": route_list}
