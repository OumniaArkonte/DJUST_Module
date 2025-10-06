# =============================
# main.py - DJUST Order-to-Cash API
# =============================

import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from fastapi import APIRouter


# Import du module principal
from Modules.Order_to_Cash_Orchestrator import (
    OrderToCashTeam,
    OrderIntakeAgent,
    InventoryAgent,
    PaymentAgent,
    ExceptionAgent,
    CoordinatorAgent,
)


# =============================
# Initialisation FastAPI
# =============================
app = FastAPI(
    title="DJUST Order-to-Cash Orchestrator API",
    description="API orchestrant les agents du module Order-to-Cash pour DJUST.",
    version="1.0.0",
)

# Autoriser les requêtes cross-origin (pour interface web ou front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# Modèles Pydantic pour validation
# =============================
class Order(BaseModel):
    order_id: int
    customer: str
    products: List[str]
    status: str = "NEW"

class OrderProcessRequest(BaseModel):
    orders: List[Order]

class PaymentRequest(BaseModel):
    order_id: int
    invoice_id: str = None

class ExceptionRequest(BaseModel):
    order_id: int
    error: str

# =============================
# Agents mapping
# =============================
AGENT_MAP = {
    "order_intake": OrderIntakeAgent,
    "inventory": InventoryAgent,
    "payment": PaymentAgent,
    "exception": ExceptionAgent,
    "coordinator": CoordinatorAgent,
}

# =============================
# Routes API
# =============================

@app.get("/")
def home():
    return {"message": "✅ DJUST Order-to-Cash Orchestrator API is running."}


# ---- ORDER INTAKE ----
@app.post("/api/order/validate")
def validate_orders(req: OrderProcessRequest):
    try:
        response = OrderIntakeAgent.run(
            input={"role": "user", "content": json.dumps([order.dict() for order in req.orders])}
        )
        return {"agent": "OrderIntakeAgent", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- INVENTORY ----
@app.post("/api/inventory/check")
def check_inventory(req: OrderProcessRequest):
    try:
        product_ids = [sku for order in req.orders for sku in order.products]
        response = InventoryAgent.run(
            input={"role": "user", "content": json.dumps({"product_ids": product_ids})}
        )
        return {"agent": "InventoryAgent", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- PAYMENT ----
@app.post("/api/payment/process")
def process_payment(req: PaymentRequest):
    try:
        response = PaymentAgent.run(
            input={"role": "user", "content": json.dumps(req.dict())}
        )
        return {"agent": "PaymentAgent", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- EXCEPTION ----
@app.post("/api/exception/handle")
def handle_exception(req: ExceptionRequest):
    try:
        response = ExceptionAgent.run(
            input={"role": "user", "content": json.dumps(req.dict())}
        )
        return {"agent": "ExceptionAgent", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- COORDINATOR ----
@app.post("/api/coordinator/summary")
def generate_summary(req: OrderProcessRequest):
    try:
        product_ids = [sku for order in req.orders for sku in order.products]
        input_data = {
            "orders": [order.dict() for order in req.orders],
            "inventory": {"product_ids": product_ids},
            "payments": [{"order_id": o.order_id} for o in req.orders],
            "exceptions": [],
        }
        response = CoordinatorAgent.run(input={"role": "user", "content": json.dumps(input_data)})
        return {"agent": "CoordinatorAgent", "result": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- TEAM ----
@app.get("/team/info")
def get_team_info():
    """Retourne la configuration complète de l’équipe Order-to-Cash."""
    return {
        "team_name": OrderToCashTeam.name,
        "description": OrderToCashTeam.description,
        "members": [member.name for member in OrderToCashTeam.members],
    }


@app.post("/team/query")
def query_team(message: Dict[str, str]):
    """Envoie une requête à l’équipe complète (multi-agents)."""
    try:
        user_message = message.get("message", "")
        result = OrderToCashTeam.run(input={"role": "user", "content": user_message})
        return {"team": OrderToCashTeam.name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



router = APIRouter(prefix="/api", tags=["Dashboard"])

@router.get("/dashboard/summary")
def get_summary():
    return {
        "total_orders": 120,
        "active_inventory": 8,
        "payments_total": 35700,
        "active_exceptions": 3,
        "exceptions_today": 1,
    }

@router.get("/order/all")
def get_orders():
    return [
        {"order_id": 101, "customer": "Alice", "total": 1200, "status": "validated"},
        {"order_id": 102, "customer": "Bob", "total": 800, "status": "pending"},
        {"order_id": 103, "customer": "Charlie", "total": 950, "status": "failed"},
        {"order_id": 104, "customer": "David", "total": 1350, "status": "validated"},
    ]

@router.get("/exceptions/active")
def get_exceptions():
    return [
        {"order_id": 103, "type": "Payment", "error": "Card declined", "status": "active"},
        {"order_id": 110, "type": "Inventory", "error": "Out of stock", "status": "active"},
        {"order_id": 120, "type": "Billing", "error": "Invoice mismatch", "status": "resolved"},
    ]





# =============================
# Lancement
# =============================
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting DJUST Order-to-Cash API...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
