import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Candidate, Recruiter, Admin, Job, Application, Swipe, Contract, Payment, Message

app = FastAPI(title="Flames.blue API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Flames.blue backend running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "Unknown"
            try:
                cols = db.list_collection_names()
                response["collections"] = cols
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# ---------- Reference data ----------
@app.get("/meta/specialties")
def meta_specialties():
    specialties = [
        "ICU","Emergency","Pediatrics","Oncology","Cardiology","Neurology","Orthopedics","Dialysis","Surgery","Anesthesiology","Midwifery","Geriatrics","Home Health","Infection Control","Radiology","Respiratory Therapy","Labor & Delivery","NICU","PICU","Phlebotomy","Wound Care","Psychiatry","Telemetry","Cath Lab","OR Circulator","PACU","Ambulatory Care","Case Management","Occupational Therapy","Physical Therapy","Medical-Surgical","Endoscopy","Dermatology","ENT","Urology","Gastroenterology","Hematology","Transplant","Burn Unit","Rehabilitation","Public Health","School Nursing","Triage","IV Therapy","Pain Management","Palliative Care","Nephrology","HIV/AIDS","Diabetes Education","Cardiothoracic","Plastic Surgery","Oral Surgery","OB/GYN","Neonatal","Nurse Educator","Nurse Practitioner","Clinical Research","Dental Assistant","Lab Technician","X-Ray Technician","Paramedic","Pharmacy Technician","Medical Assistant","Sonography","Echo Tech","Cath Tech"
    ]
    return specialties

@app.get("/meta/gcc-countries")
def meta_gcc():
    return ["KSA","UAE","Qatar","Oman","Bahrain","Kuwait"]

# ---------- Auth-lite (mock) ----------
class SignupCandidate(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None

@app.post("/auth/candidate/signup")
def signup_candidate(payload: SignupCandidate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    # Minimal create; email can be added later in onboarding
    doc = {
        "full_name": payload.full_name,
        "email": payload.email,
        "phone": payload.phone,
        "role": "candidate",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    inserted = db["candidate"].insert_one(doc)
    return {"id": str(inserted.inserted_id)}

# ---------- Onboarding endpoints ----------
class OnboardingStep(BaseModel):
    candidate_id: str
    data: Dict[str, Any]

@app.post("/onboarding/step/{step}")
def save_onboarding_step(step: int, payload: OnboardingStep):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        oid = ObjectId(payload.candidate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate_id")
    update_doc = {**payload.data, "updated_at": datetime.utcnow()}
    result = db["candidate"].update_one({"_id": oid}, {"$set": update_doc})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return {"ok": True, "step": step}

# ---------- Jobs ----------
@app.post("/jobs")
def create_job(job: Job):
    job_id = create_document("job", job)
    return {"id": job_id}

@app.get("/jobs")
def list_jobs(limit: int = 20):
    jobs = get_documents("job", {}, limit)
    for j in jobs:
        j["_id"] = str(j.get("_id"))
    return jobs

# ---------- Swipes (job discovery) ----------
@app.post("/swipes")
def swipe(s: Swipe):
    sid = create_document("swipe", s)
    return {"id": sid}

# ---------- Applications ----------
@app.post("/applications")
def apply(apply: Application):
    aid = create_document("application", apply)
    return {"id": aid}

# ---------- Fit Score & Compliance (mock) ----------
@app.get("/ai/fit-score/{candidate_id}/{job_id}")
def fit_score(candidate_id: str, job_id: str):
    score = (hash(candidate_id + job_id) % 100)
    return {"fit_score": score}

@app.get("/ai/compliance/{candidate_id}")
def compliance(candidate_id: str):
    flags = ["visa_pending"]
    return {"flags": flags}

# ---------- Resume upload (mock extract) ----------
@app.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    contents = await file.read()
    size_kb = round(len(contents) / 1024, 2)
    return {
        "file_name": file.filename,
        "size_kb": size_kb,
        "extracted": {
            "full_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "experience_years": 5,
            "specialties": ["ICU", "Emergency"],
        }
    }

# ---------- Contracts & Payments (mock flow) ----------
@app.post("/contracts")
def create_contract(contract: Contract):
    cid = create_document("contract", contract)
    return {"id": cid, "status": contract.status}

@app.post("/payments")
def create_payment(payment: Payment):
    pid = create_document("payment", payment)
    return {"id": pid, "status": payment.status}

# ---------- Admin views ----------
@app.get("/admin/candidates")
def admin_candidates(limit: int = 50):
    docs = get_documents("candidate", {}, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

@app.get("/admin/recruiters")
def admin_recruiters(limit: int = 50):
    docs = get_documents("recruiter", {}, limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
