from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

company_router = APIRouter()

SUREPASS_SEARCH_API = "https://kyc-api.surepass.io/api/v1/corporate/company-details"
SUREPASS_TOKEN = os.getenv("SUREPASS_TOKEN")  # Use sandbox token for dev

# Request model
class CompanySearchRequest(BaseModel):
    cin: str

# -------------------------
# POST /search-company
# -------------------------
@company_router.post("/search-company")
def search_company(req: CompanySearchRequest):
    try:
        response = requests.post(
            SUREPASS_SEARCH_API,
            headers={
                "Authorization": f"Bearer {SUREPASS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"id_number": req.cin}
        )

        res_json = response.json()

        if not res_json.get("success"):
            raise HTTPException(status_code=404, detail="Company not found")

        data = res_json["data"]["details"]["company_info"]
        return {
            "company_name": res_json["data"]["company_name"],
            "cin": data["cin"],
            "date_of_incorporation": data["date_of_incorporation"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
