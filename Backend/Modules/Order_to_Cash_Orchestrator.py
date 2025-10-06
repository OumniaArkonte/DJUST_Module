# module.py - Order-to-Cash Orchestrator Module for DJUST

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from agno.agent import Agent
from agno.team.team import Team
from agno.models.mistral import MistralChat
from agno.tools.file import FileTools
from agno.tools.calculator import CalculatorTools

from agno.knowledge.reader.markdown_reader import MarkdownReader
from agno.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.knowledge.embedder.mistral import MistralEmbedder
from agno.models.google import Gemini

# Import des outils custom
try:
    from .tools import (
        fetch_orders,
        update_order_status,
        query_inventory,
        create_purchase_order,
        generate_invoice,
        call_djust_pay,
        notify,
        kb_ingest_indexer,
    )
except ImportError:
    from tools import (
        fetch_orders,
        update_order_status,
        query_inventory,
        create_purchase_order,
        generate_invoice,
        call_djust_pay,
        notify,
        kb_ingest_indexer,
    )

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()


# ----------------------------
# Fonction helper : Choisir le modèle actif
# ----------------------------
def get_model(model_size="small"):
    mistral_key = os.getenv("MISTRAL_API_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")

    try:
        if mistral_key:
            if model_size == "large":
                return MistralChat(id="mistral-large-latest", api_key=mistral_key)
            else:
                return MistralChat(id="mistral-small-latest", api_key=mistral_key)
        else:
            raise ValueError("Missing Mistral key.")
    except Exception as e:
        print(f"[⚠️] Mistral indisponible ({e}), fallback vers Gemini.")
        if gemini_key:
            return Gemini(id="gemini-1.5-pro", api_key=gemini_key)
        else:
            raise RuntimeError("❌ Aucun modèle disponible (ni Mistral ni Gemini).")


# ----------------------------
# Knowledge Base
# ----------------------------
db_url = "postgresql+psycopg://ai:ai@localhost:5433/ai"

markdown_reader = MarkdownReader(name="Order Exception Reader")

vector_db = PgVector(
    table_name="order_exception_docs",
    db_url=db_url,
    embedder=MistralEmbedder(api_key=os.getenv("MISTRAL_API_KEY"), dimensions=1024)
)

knowledge_base = Knowledge(
    name="Order Exception KB",
    vector_db=vector_db,
    max_results=5
)

# =============================
# Agent 1: Order Intake Agent
# =============================
OrderIntakeAgent = Agent(
    name="Order Intake Agent",
    model=get_model("large"),
    tools=[
        fetch_orders,
        update_order_status,
        notify,
        FileTools(base_dir=Path(os.path.join(os.path.dirname(__file__), "documents"))),
        kb_ingest_indexer,
    ],
    description="""
    Agent spécialisé dans la réception et validation initiale des commandes.
    """,
    instructions="""
    Vous êtes OrderIntakeAgent, spécialiste de la validation des commandes.

    ## Agent Responsibilities
    1. Récupérer les nouvelles commandes.
    2. Vérifier les champs obligatoires (client, adresse, produits).
    3. Marquer les commandes complètes comme READY.
    4. En cas d'erreur, notifier ExceptionAgent.

    ## Tool Usage Guidelines
    - fetch_orders pour récupérer les commandes.
    - update_order_status pour changer le statut.
    - notify pour alerter sur erreurs.
    - FileTools pour gérer les documents de règles métier.
    - kb_ingest_indexer pour consulter/référencer règles métier.

    ## Sortie attendue
    - commandes validées
    - commandes en erreur
    """,
    markdown=True,
    knowledge=knowledge_base,
)

# =============================
# Agent 2: Inventory Agent
# =============================
InventoryAgent = Agent(
    name="Inventory Agent",
    model=get_model("large"),
    tools=[
        query_inventory,
        create_purchase_order,
        notify,
    ],
    description="""
    Agent spécialisé dans la gestion et suivi des stocks.
    """,
    instructions="""
    Vous êtes InventoryAgent, spécialiste de la gestion des stocks.

    ## Agent Responsibilities
    1. Vérifier la disponibilité des produits.
    2. Créer des demandes de réapprovisionnement si nécessaire.
    3. Notifier le client en cas de délai.

    ## Tool Usage Guidelines
    - query_inventory pour vérifier stock.
    - create_purchase_order pour réapprovisionnement.
    - notify pour communication.

    ## Sortie attendue
    - produits disponibles
    - produits en rupture
    """,
    markdown=True,
    knowledge=knowledge_base,
)

# =============================
# Agent 3: Payment Agent
# =============================
PaymentAgent = Agent(
    name="Payment Agent",
    model=get_model("large"),
    tools=[
        generate_invoice,
        call_djust_pay,
        notify,
    ],
    description="""
    Agent responsable de la facturation et du paiement via DJUST Pay.
    """,
    instructions="""
    Vous êtes PaymentAgent, spécialiste de la facturation et encaissement.

    ## Agent Responsibilities
    1. Générer une facture pour la commande.
    2. Lancer le paiement via DJUST Pay.
    3. Notifier ExceptionAgent en cas d'échec.

    ## Tool Usage Guidelines
    - generate_invoice pour créer facture.
    - call_djust_pay pour simuler paiement.
    - notify pour alertes.

    ## Sortie attendue
    - facture générée
    - paiement effectué / échoué
    """,
    markdown=True,
    knowledge=knowledge_base,
)

# =============================
# Agent 4: Exception Agent
# =============================
ExceptionAgent = Agent(
    name="Exception Agent",
    model=get_model("large"),
    tools=[notify, FileTools(base_dir=Path(os.path.join(os.path.dirname(__file__), "documents")))],
    description="""
    Agent dédié au traitement des exceptions (erreurs de commande, paiement refusé, rupture de stock).
    """,
    instructions="""
    Vous êtes ExceptionAgent, spécialiste du traitement des anomalies.

    ## Agent Responsibilities
    1. Identifier l'erreur rencontrée.
    2. Consulter la Knowledge Base pour les règles métier.
    3. Proposer une solution (réessayer, escalader, alternative produit).

    ## Tool Usage Guidelines
    - notify pour communiquer la solution.
    - FileTools pour consulter les documents de règles métier.
    - consulter KnowledgeBase pour règles métier.

    ## Sortie attendue
    - solution proposée
    """,
    markdown=True,
    knowledge=knowledge_base,
)

# =============================
# Agent 5: Coordinator Agent
# =============================
CoordinatorAgent = Agent(
    name="Coordinator Agent",
    model=get_model("large"),
    tools=[CalculatorTools()],
    description="""
    Agent coordinateur qui orchestre le processus Order-to-Cash.
    """,
    instructions="""
    Vous êtes CoordinatorAgent, spécialiste de la supervision du flux Order-to-Cash.

    ## Agent Responsibilities
    1. Superviser et décomposer le processus complet.
    2. Envoyer les commandes à OrderIntakeAgent → InventoryAgent → PaymentAgent.
    3. Diriger les problèmes vers ExceptionAgent.
    4. Fournir un résumé final clair au client.

    ## Tool Usage Guidelines
    - CalculatorTools() pour calculs si nécessaire.
    - Communication avec tous les agents pour coordination.

    ## Sortie attendue
    - rapport final client
    """,
    markdown=True,
    knowledge=knowledge_base,
)

# =============================
# Team: Order-to-Cash Team
# =============================
OrderToCashTeam = Team(
    name="OrderToCash",
    model=get_model("large"),
    members=[
        OrderIntakeAgent,
        InventoryAgent,
        PaymentAgent,
        ExceptionAgent,
        CoordinatorAgent,
    ],
    description="""
    Module complet automatisant le flux Order-to-Cash pour DJUST :
    commande → stock → paiement → exception → confirmation.
    """,
    instructions="""
    Le module orchestre 5 agents spécialisés :
    - Order Intake Agent : validation initiale.
    - Inventory Agent : vérification stock.
    - Payment Agent : facturation et paiement.
    - Exception Agent : traitement des anomalies.
    - Coordinator Agent : supervision globale.

    Workflow recommandé :
    1) OrderIntakeAgent → valider la commande.
    2) InventoryAgent → vérifier stock.
    3) PaymentAgent → facturer et encaisser.
    4) ExceptionAgent → gérer les erreurs.
    5) CoordinatorAgent → rapport final client.
    """,
    markdown=True,
    knowledge=knowledge_base,
)


# =============================
# Code d’exemple (exécution locale)
# =============================
if __name__ == "__main__":
    print("Order-to-Cash Orchestrator Module loaded successfully ✅")
    
    # Exemple de commandes
    orders = [
        {"order_id": 1, "customer": "John Doe", "products": ["SKU1", "SKU2"], "status": "NEW"},
        {"order_id": 2, "customer": "Jane Smith", "products": ["SKU3"], "status": "NEW"},
    ]
    
    product_ids = [sku for order in orders for sku in order["products"]]
    
    # Tests agents
    OrderIntakeAgent.print_response(input={"role": "user", "content": "Process a new order with multiple SKUs."})
    InventoryAgent.print_response(input={"role": "user", "content": json.dumps({"product_ids": product_ids})})
    for order in orders:
        PaymentAgent.print_response(input={"role": "user", "content": json.dumps({"order_id": order["order_id"]})})
    
    exceptions = [{"order_id": 2, "error": "payment failure"}]
    for exc in exceptions:
        ExceptionAgent.print_response(input={"role": "user", "content": json.dumps(exc)})
    
    coordinator_input = {
        "orders": orders,
        "inventory": {"product_ids": product_ids},
        "payments": [{"order_id": order["order_id"]} for order in orders],
        "exceptions": exceptions,
    }
    CoordinatorAgent.print_response(input={"role": "user", "content": json.dumps(coordinator_input)})
    
    print("✅ Full Order-to-Cash workflow executed successfully!")
