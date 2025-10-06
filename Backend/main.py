import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import json
import markdown
import io
import sys
import pandas as pd
import re

# Import ton module Order-to-Cash
from Modules.Order_to_Cash_Orchestrator import (
    OrderIntakeAgent,
    InventoryAgent,
    PaymentAgent,
    ExceptionAgent,
    CoordinatorAgent,
)

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(
    page_title="Order-to-Cash Module",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS pour styling
st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
        .chat-header { background: #0f172a; border-radius: 12px; padding: 1.25rem 1.5rem; border: 1px solid #334155; }
        .chat-message { display: flex; align-items: flex-start; margin-bottom: 1.1rem; }
        .chat-message.user { flex-direction: row-reverse; }
        .chat-message .avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1rem; margin: 0 0.75rem; flex-shrink: 0; }
        .chat-message.user .avatar { background: #0ea5e9; color: #fff; }
        .chat-message.bot .avatar { background: #0369a1; color: #fff; }
        .chat-message .content { background: #334155; color: #f1f5f9; padding: 0.85rem 1.1rem; border-radius: 12px; max-width: 72%; border: 1px solid #475569; }
        .chat-message.user .content { background: #0ea5e9; color: #fff; border-color: #0ea5e9; }
        .chat-message .timestamp { font-size: 0.72rem; color: #94a3b8; margin-top: 0.35rem; text-align: right; }
        .chat-message.user .timestamp { color: rgba(255,255,255,.85); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Session state
# ----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "orders" not in st.session_state:
    st.session_state.orders = []

# ----------------------------
# Fonctions utilitaires
# ----------------------------
def safe_str(obj):
    if obj is None:
        return ""
    elif isinstance(obj, (dict, list)):
        return json.dumps(obj, indent=2, ensure_ascii=False)
    return str(obj)

def display_chat_message(message, is_user=True):
    message = safe_str(message)
    html_message = markdown.markdown(message, extensions=['nl2br'])
    
    if is_user:
        st.markdown(
            f"""
            <div class="chat-message user">
                <div class="avatar">RE</div>
                <div class="content">
                    {html_message}
                    <div class="timestamp">just now</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-message bot">
                <div class="avatar">AI</div>
                <div class="content">
                    {html_message}
                    <div class="timestamp">AI Team</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def save_uploaded_file(uploaded_file):
    documents_dir = os.path.join("Modules", "documents")
    os.makedirs(documents_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uploaded_file.name}"
    file_path = os.path.join(documents_dir, filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

# ----------------------------
# Capture et affichage propre des agents
# ----------------------------
def capture_agent_output(agent, input_data):
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    try:
        agent.print_response(input=input_data)
        output = mystdout.getvalue()
        if not output.strip():
            return "(No response from agent)"
        return output
    except Exception as e:
        err_msg = str(e)
        if "Status 429" in err_msg:
            return f"⚠️ L'agent {agent.__class__.__name__} n'a pas pu répondre (limite API atteinte)."
        return f"⚠️ Error from {agent.__class__.__name__}: {err_msg}"
    finally:
        sys.stdout = old_stdout

def human_readable_agent_output(output):
    """
    Transforme la sortie brute d'un agent en langage naturel lisible.
    Supprime les Tool Calls et autres détails internes.
    """
    
    output = re.sub(r'(Tool Calls\s+|Message\s+).*', '', output, flags=re.DOTALL)
    
    output = re.sub(r'\x1b\[[0-9;]*m', '', output)
    output = re.sub(r'[^\x20-\x7E\n,{}[\]]+', ' ', output)

    try:
        data = json.loads(output)
        lines = []

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    order_id = item.get("order_id", "")
                    customer = item.get("customer", "")
                    products = ", ".join(item.get("products", []))
                    status = item.get("status", "")
                    lines.append(f"Commande #{order_id} pour {customer} avec produits [{products}] — Statut : {status}")
                else:
                    lines.append(str(item))
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list):
                    v = ", ".join(map(str, v))
                lines.append(f"{k.capitalize()}: {v}")
        else:
            lines.append(str(data))

        return "\n".join(lines)
    except Exception:
        return output.strip()

def display_agent_output(output, agent_name="Agent"):
    """
    Affiche proprement la sortie d'un agent en langage naturel
    """
    readable_output = human_readable_agent_output(output)
    st.markdown(f"### {agent_name}")
    st.text(readable_output)

# ----------------------------
# Interface de chat
# ----------------------------
st.markdown(
    f"""
    <div class="chat-header">
        <div class="module-tag">💰 Order-to-Cash</div>
        <h1>Chat with Order-to-Cash Module</h1>
        <p class="description">Automated order processing workflow</p>
        <p class="description"><strong>Team:</strong> Order-to-Cash Team</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Historique chat
for message in st.session_state.chat_history:
    display_chat_message(message["content"], message["is_user"])

# Message de bienvenue
if not st.session_state.chat_history:
    display_chat_message(
        "Hello! I'm your Order-to-Cash AI assistant. How can I help you today?", 
        is_user=False
    )

# ----------------------------
# Input utilisateur
# ----------------------------
user_input = st.text_area("Your message:", height=80)
if st.button("Send") and user_input:
    st.session_state.chat_history.append({"content": user_input, "is_user": True})
    display_chat_message(user_input, is_user=True)

    # ---- Pipeline agents ----
    # 1️⃣ Order Intake Agent
    intake_response = capture_agent_output(OrderIntakeAgent, {"role": "user", "content": user_input})
    display_agent_output(intake_response, "Order Intake Agent")

    # Stocke les commandes simulées
    orders = [
        {"order_id": 1, "customer": "John Doe", "products": ["SKU1", "SKU2"], "status": "NEW"},
        {"order_id": 2, "customer": "Jane Smith", "products": ["SKU3"], "status": "NEW"},
    ]
    st.session_state.orders = orders

    # 2️⃣ Inventory Agent
    product_ids = [sku for order in orders for sku in order["products"]]
    inventory_response = capture_agent_output(InventoryAgent, {"role": "user", "content": json.dumps({"product_ids": product_ids})})
    display_agent_output(inventory_response, "Inventory Agent")

    # 3️⃣ Payment Agent
    for order in orders:
        payment_response = capture_agent_output(PaymentAgent, {"role": "user", "content": json.dumps({"order_id": order["order_id"]})})
        display_agent_output(payment_response, f"Payment Agent - Order {order['order_id']}")

    # 4️⃣ Exception Agent
    exceptions = [{"order_id": 2, "error": "payment failure"}]
    for exc in exceptions:
        exception_response = capture_agent_output(ExceptionAgent, {"role": "user", "content": json.dumps(exc)})
        display_agent_output(exception_response, f"Exception Agent - Order {exc['order_id']}")

    # 5️⃣ Coordinator Agent
    coordinator_input = {
        "orders": orders,
        "inventory": {"product_ids": product_ids},
        "payments": [{"order_id": order["order_id"]} for order in orders],
        "exceptions": exceptions,
    }
    coordinator_response = capture_agent_output(CoordinatorAgent, {"role": "user", "content": json.dumps(coordinator_input)})
    display_agent_output(coordinator_response, "Coordinator Agent")

# ----------------------------
# Upload de fichiers
# ----------------------------
uploaded_file = st.file_uploader("Upload a document")
if uploaded_file:
    file_path = save_uploaded_file(uploaded_file)
    st.success(f"File saved to: {file_path}")
