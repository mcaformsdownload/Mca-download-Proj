# from fastapi import FastAPI
# from auth import auth_router
# from company import company_router
# from order import order_router
# from scheduler import start_scheduler
# from fastapi.middleware.cors import CORSMiddleware


# app = FastAPI()

# # Include Auth & Order APIs
# app.include_router(auth_router)
# app.include_router(company_router)
# app.include_router(order_router)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["https://downloadmcafiles.com"],  # Or replace * with ["http://localhost:4200"]
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # Start background scheduler
# start_scheduler()

# @app.get("/")
# def home():
#     return {"message": "Welcome to Company Docs API"}



from fastapi import FastAPI
from auth import auth_router
from company import company_router
from order import order_router
from scheduler import start_scheduler
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

logger.info("Starting the FastAPI application...")

app = FastAPI()

# Include routers
logger.info("Including auth, company, and order routers.")
app.include_router(auth_router)
app.include_router(company_router)
app.include_router(order_router)

# Add CORS middleware
logger.info("Adding CORS middleware.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://downloadmcafiles.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start background scheduler
logger.info("Starting background scheduler.")
start_scheduler()

@app.get("/")
def home():
    logger.info("Received request at / endpoint.")
    return {"message": "Welcome to Company Docs API"}
