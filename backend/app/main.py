from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, field_validator
from typing import Optional
import re

app = FastAPI()


# =========================
# Health Check
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}


# =========================
# Schema Input
# =========================
class MenuCreate(BaseModel):
    nama: str
    sku: str
    kategori: str

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value):
        if not re.fullmatch(r"KOPI-\d{3}", value):
            raise ValueError(
                "SKU harus format KOPI-000"
            )
        return value

    @field_validator("kategori")
    @classmethod
    def validate_kategori(cls, value):
        allowed = [
            "kopi",
            "non-kopi",
            "makanan"
        ]

        if value not in allowed:
            raise ValueError(
                "Kategori harus kopi, non-kopi, atau makanan"
            )

        return value


# =========================
# Schema Output
# =========================
class MenuResponse(BaseModel):
    id: int
    nama: str
    sku: str
    kategori: str


# =========================
# Simulasi Database
# =========================
db = []
next_id = 1


# =========================
# POST /api/menu
# =========================
@app.post(
    "/api/menu",
    response_model=MenuResponse,
    status_code=201
)
def create_menu(
    data: MenuCreate,
    response: Response
):
    global next_id

    menu = {
        "id": next_id,
        "nama": data.nama,
        "sku": data.sku,
        "kategori": data.kategori
    }

    db.append(menu)

    response.headers["Location"] = (
        f"/api/menu/{next_id}"
    )

    next_id += 1

    return menu


# =========================
# GET /api/menu
# =========================
@app.get(
    "/api/menu",
    response_model=list[MenuResponse]
)
def get_menu(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
):
    result = db

    if search:
        result = [
            item
            for item in result
            if search.lower()
            in item["nama"].lower()
        ]

    return result[
        skip:skip + limit
    ]


# =========================
# GET /api/menu/{id}
# =========================
@app.get(
    "/api/menu/{id}",
    response_model=MenuResponse
)
def get_menu_by_id(id: int):

    for item in db:
        if item["id"] == id:
            return item

    raise HTTPException(
        status_code=404,
        detail="Menu tidak ditemukan"
    )