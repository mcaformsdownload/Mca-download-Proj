from fastapi import FastAPI
from auth import auth_router
from company import company_router
from order import order_router
from scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Include Auth & Order APIs
app.include_router(auth_router)
app.include_router(company_router)
app.include_router(order_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://downloadmcafiles.com","https://company-docs-frontend.netlify.app/login"],  # Or replace * with ["http://localhost:4200"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Start background scheduler
start_scheduler()

@app.get("/")
def home():
    return {"message": "Welcome to Company Docs API"}

