# =============================
# tools.py - Order-to-Cash Orchestrator Module
# =============================
from agno.tools import tool
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


# =============================
# Tool 1: fetch_orders (OrderIntakeAgent)
# =============================
@tool(
    name="fetch_orders",
    description="Récupère les nouvelles commandes depuis le système",
    show_result=True,
)
def fetch_orders() -> List[Dict[str, Any]]:
    sample_orders = [
        {"order_id": 1, "customer": "John Doe", "products": ["SKU1", "SKU2"], "status": "NEW"},
        {"order_id": 2, "customer": "Jane Smith", "products": ["SKU3"], "status": "NEW"},
    ]
    return sample_orders


# =============================
# Tool 2: update_order_status (OrderIntakeAgent)
# =============================
@tool(
    name="update_order_status",
    description="Met à jour le statut d'une commande",
    show_result=True,
)
def update_order_status(order_id: int, status: str) -> Dict[str, Any]:
    return {
        "order_id": order_id,
        "new_status": status,
        "updated_at": datetime.now().isoformat(),
    }


# =============================
# Tool 3: notify (All Agents)
# =============================
@tool(
    name="notify",
    description="Envoie une notification interne",
    show_result=True,
)
def notify(message: str, recipient: Optional[str] = None) -> Dict[str, Any]:
    return {
        "message_sent": message,
        "recipient": recipient,
        "sent_at": datetime.now().isoformat(),
    }


# =============================
# Tool 4: query_inventory (InventoryAgent)
# =============================
@tool(
    name="query_inventory",
    description="Vérifie la disponibilité des produits en stock",
    show_result=True,
)
def query_inventory(product_id: str) -> Dict[str, Any]:
    available = random.choice([True, False])
    return {
        "product_id": product_id,
        "available": available,
        "checked_at": datetime.now().isoformat(),
    }


# =============================
# Tool 5: create_purchase_order (InventoryAgent)
# =============================
@tool(
    name="create_purchase_order",
    description="Crée un bon de commande pour réapprovisionnement",
    show_result=True,
)
def create_purchase_order(product_id: str, qty: int) -> Dict[str, Any]:
    return {
        "po_created": True,
        "product_id": product_id,
        "qty": qty,
        "created_at": datetime.now().isoformat(),
    }


# =============================
# Tool 6: generate_invoice (PaymentAgent)
# =============================
@tool(
    name="generate_invoice",
    description="Génère une facture pour une commande",
    show_result=True,
)
def generate_invoice(order_id: int) -> Dict[str, Any]:
    invoice_id = f"INV-{order_id}-{random.randint(1000,9999)}"
    return {
        "invoice_id": invoice_id,
        "order_id": order_id,
        "generated_at": datetime.now().isoformat(),
    }


# =============================
# Tool 7: call_djust_pay (PaymentAgent)
# =============================
@tool(
    name="call_djust_pay",
    description="Simule le paiement via DJUST Pay",
    show_result=True,
)
def call_djust_pay(invoice_id: str) -> Dict[str, Any]:
    status = random.choice(["PAID", "FAILED"])
    return {
        "invoice_id": invoice_id,
        "status": status,
        "processed_at": datetime.now().isoformat(),
    }


# =============================
# Tool 8: supplier_web_scraper (Optional: DataCollectorAgent)
# =============================
@tool(
    name="supplier_web_scraper",
    description="Scrape multi-sources (sites fournisseurs/catalogues web) et normalise les champs produit, prix et conditions.",
    show_result=True,
)
def supplier_web_scraper(query: str, location: Optional[str] = None, max_results: int = 20) -> Dict[str, Any]:
    sample_results = [
        {
            "supplier": "ABC Supplies",
            "product": "Steel Rods",
            "unit_price": 12.5,
            "currency": "EUR",
            "min_order_qty": 100,
            "delivery_time_days": 7,
            "source": "web",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
        {
            "supplier": "XYZ Metals",
            "product": "Steel Rods",
            "unit_price": 11.8,
            "currency": "EUR",
            "min_order_qty": 200,
            "delivery_time_days": 10,
            "source": "web",
            "date": datetime.now().strftime("%Y-%m-%d"),
        },
    ]
    return {
        "query": query,
        "location": location,
        "results": sample_results[:max_results],
        "collected_at": datetime.now().isoformat(),
    }


# =============================
# Tool 9: procurement_data_cleaner (Optional: Inventory / Analytics)
# =============================
@tool(
    name="procurement_data_cleaner",
    description="Nettoie et harmonise les données d’achats et identifie les anomalies.",
    show_result=True,
)
def procurement_data_cleaner(raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    cleaned: List[Dict[str, Any]] = []
    anomalies: List[str] = []
    for item in raw_data:
        price = item.get("unit_price", 0)
        if price <= 0:
            anomalies.append(f"Invalid price: {price} for {item.get('product')}")
            continue
        cleaned.append(item)
    return {
        "cleaned_data": cleaned,
        "anomalies": anomalies,
        "processed_at": datetime.now().isoformat(),
    }


# =============================
# Tool 10: price_benchmark_engine (Optional: Inventory / Analytics)
# =============================
@tool(
    name="price_benchmark_engine",
    description="Compare les prix unitaires par fournisseur et calcule les économies potentielles.",
    show_result=True,
)
def price_benchmark_engine(cleaned_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not cleaned_data:
        return {"error": "No data provided"}
    min_price = min(item["unit_price"] for item in cleaned_data)
    avg_price = sum(item["unit_price"] for item in cleaned_data) / len(cleaned_data)
    recommendations = [
        f"Supplier {item['supplier']} offers below average price: {item['unit_price']} EUR"
        for item in cleaned_data if item["unit_price"] <= avg_price
    ]
    return {
        "min_price": min_price,
        "avg_price": round(avg_price, 2),
        "recommendations": recommendations,
        "benchmarked_at": datetime.now().isoformat(),
    }


# =============================
# Tool 11: negotiation_assistant (Optional: Payment / Procurement)
# =============================
@tool(
    name="negotiation_assistant",
    description="Génère des arguments de négociation basés sur benchmarks et historiques achats.",
    show_result=True,
)
def negotiation_assistant(supplier: str, target_price: float, current_price: float) -> Dict[str, Any]:
    margin = round(((current_price - target_price) / current_price) * 100, 2)
    arguments = [
        "Market benchmark shows lower prices available.",
        f"Similar suppliers offer {target_price} EUR/unit.",
        f"Reducing price by {margin}% aligns with market standards.",
    ]
    return {
        "supplier": supplier,
        "current_price": current_price,
        "target_price": target_price,
        "negotiation_arguments": arguments,
        "prepared_at": datetime.now().isoformat(),
    }


# =============================
# Tool 12: Knowledge Base Ingest & Indexer (All Agents)
# =============================
@tool(
    name="kb_ingest_indexer",
    description="Ingestion et indexation vecteur de documents/datasets achats dans la base de connaissance.",
    show_result=True,
)
def kb_ingest_indexer(paths: List[str], collection: str, recreate: bool = False) -> Dict[str, Any]:
    return {
        "collection": collection,
        "ingested_items": len(paths),
        "recreated": recreate,
        "indexed_at": datetime.now().isoformat(),
    }
