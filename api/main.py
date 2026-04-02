from decimal import Decimal
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from gix import service

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"

app = FastAPI(title="GIX Purchase Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PurchaseCreate(BaseModel):
    team_number: int = Field(..., ge=1)
    cfo_name: str
    purchase_link: str
    price_per_item: Decimal = Field(..., ge=0)
    quantity: int = Field(..., ge=1)
    notes: str = ""
    instructor_approved: bool = False


class StatusUpdate(BaseModel):
    status: str


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/purchases")
def api_list_purchases():
    return service.list_purchases()


@app.get("/api/teams")
def api_list_teams():
    return service.list_teams()


@app.post("/api/purchases")
def api_create_purchase(body: PurchaseCreate):
    try:
        return service.create_purchase(
            team_number=body.team_number,
            cfo_name=body.cfo_name,
            purchase_link=body.purchase_link,
            price_per_item=body.price_per_item,
            quantity=body.quantity,
            notes=body.notes,
            instructor_approved=body.instructor_approved,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.patch("/api/purchases/{purchase_id}/status")
def api_update_status(purchase_id: int, body: StatusUpdate):
    try:
        return service.update_purchase_status(purchase_id, body.status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND)),
    name="static",
)
