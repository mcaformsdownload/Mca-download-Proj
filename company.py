# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# import requests
# import os
# from dotenv import load_dotenv

# load_dotenv()

# company_router = APIRouter()

# SUREPASS_SEARCH_API = "https://kyc-api.surepass.io/api/v1/corporate/company-details"
# SUREPASS_TOKEN = os.getenv("SUREPASS_TOKEN")  # Use sandbox token for dev

# # Request model
# class CompanySearchRequest(BaseModel):
#     cin: str

# # -------------------------
# # POST /search-company
# # -------------------------
# @company_router.post("/search-company")
# def search_company(req: CompanySearchRequest):
#     try:
#         response = requests.post(
#             SUREPASS_SEARCH_API,
#             headers={
#                 "Authorization": f"Bearer {SUREPASS_TOKEN}",
#                 "Content-Type": "application/json"
#             },
#             json={"id_number": req.cin}
#         )

#         res_json = response.json()

#         if not res_json.get("success"):
#             raise HTTPException(status_code=404, detail="Company not found")

#         data = res_json["data"]["details"]["company_info"]
#         return {
#             "company_name": res_json["data"]["company_name"],
#             "cin": data["cin"],
#             "date_of_incorporation": data["date_of_incorporation"]
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



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

@company_router.post("/search-company")
def search_company(req: CompanySearchRequest):
    try:
        if not SUREPASS_TOKEN:
            print("❌ SUREPASS_TOKEN is missing in environment variables")
            raise HTTPException(status_code=500, detail="Missing Surepass API token")

        print(f"🔍 Searching company with CIN: {req.cin}")
        response = requests.post(
            SUREPASS_SEARCH_API,
            headers={
                "Authorization": f"Bearer {SUREPASS_TOKEN}",
                "Content-Type": "application/json"
            },
            json={"id_number": req.cin}
        )

        print(f"✅ Surepass API Status Code: {response.status_code}")
        print(f"✅ Surepass API Response: {response.text}")

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from Surepass API")

        res_json = response.json()

        if not res_json.get("success"):
            raise HTTPException(status_code=404, detail="Company not found")

        data = res_json["data"]["details"]["company_info"]

        return {
            "company_name": res_json["data"]["company_name"],
            "cin": data["cin"],
            "date_of_incorporation": data["date_of_incorporation"]
        }

    except requests.exceptions.RequestException as req_err:
        print(f"❌ Request Exception: {req_err}")
        raise HTTPException(status_code=502, detail="Error connecting to Surepass API")

    except Exception as e:
        print(f"❌ General Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
