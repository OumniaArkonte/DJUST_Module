# Order-to-Cash Orchestrator Module for DJUST

## Overview

The **Order-to-Cash Orchestrator** automates the entire order processing workflow for DJUST, covering:

1. **Order Intake**
2. **Inventory Management**
3. **Billing and Payment**
4. **Exception Handling**
5. **Coordination and Supervision**

The module leverages large language models (LLMs) like **Mistral** or **Gemini**, a **vector-based Knowledge Base** for business rules, and various Agno and custom tools to handle each stage of the workflow.

---

## Agents

### 1. Order Intake Agent

**Description:**  
Specializes in receiving and validating incoming orders.

**Responsibilities:**

- Retrieve new orders from the system.
- Check required fields such as customer info, address, and products.
- Mark complete orders as `READY`.
- Notify the Exception Agent in case of errors.

**Tools Used:**  
`fetch_orders`, `update_order_status`, `notify`, `FileTools` (Agno), `kb_ingest_indexer`

---

### 2. Inventory Agent

**Description:**  
Manages and tracks stock availability.

**Responsibilities:**

- Check product availability in inventory.
- Create purchase orders for restocking when needed.
- Notify clients if delays are expected.

**Tools Used:**  
`query_inventory`, `create_purchase_order`, `notify`

---

### 3. Payment Agent

**Description:**  
Handles billing and payments through DJUST Pay.

**Responsibilities:**

- Generate invoices for orders.
- Process payments via DJUST Pay.
- Notify Exception Agent on payment failures.

**Tools Used:**  
`generate_invoice`, `call_djust_pay`, `notify`

---

### 4. Exception Agent

**Description:**  
Dedicated to handling errors such as order issues, payment failures, or stock shortages.

**Responsibilities:**

- Identify encountered errors.
- Consult the Knowledge Base for business rules.
- Propose a solution: retry, escalate, or suggest alternative products.

**Tools Used:**  
`notify`, `FileTools` (Agno), Knowledge Base

---

### 5. Coordinator Agent

**Description:**  
Orchestrates the full Order-to-Cash process.

**Responsibilities:**

- Supervise the end-to-end workflow.
- Route orders to specialized agents.
- Forward problems to the Exception Agent.
- Provide a clear final summary to the client.

**Tools Used:**  
`CalculatorTools` (Agno), internal communication with all agents

---

## Optional and Supporting Tools

- `supplier_web_scraper`: Collects supplier data from multiple sources and normalizes product, price, and delivery information.
- `procurement_data_cleaner`: Cleans and harmonizes procurement data, identifying anomalies.
- `price_benchmark_engine`: Compares unit prices among suppliers and provides recommendations.
- `negotiation_assistant`: Generates negotiation arguments based on historical purchases and benchmarks.
- `kb_ingest_indexer`: Ingests and indexes documents or datasets into the Knowledge Base for all agents.

---

## Knowledge Base

- **Name:** Order Exception KB  
- **Database:** PostgreSQL + PgVector  
- **Embedder:** MistralEmbedder  
- **Content:** Markdown documents on order exceptions and business rules  
- **Max Results:** 5

---

## Recommended Workflow

1. **Order Intake Agent** validates the order.
2. **Inventory Agent** checks product availability.
3. **Payment Agent** generates the invoice and processes payment.
4. **Exception Agent** handles detected errors.
5. **Coordinator Agent** supervises the workflow and provides a final client report.

---

## Technical Notes

- Agents use **Mistral** as the main LLM, with **Gemini** as a fallback.
- The module can run locally for testing or debugging.
- Agno tools (`FileTools`, `CalculatorTools`) and custom tools (`fetch_orders`, `generate_invoice`, etc.) enable full simulation of the workflow.

---

**✅ Complete module to automate DJUST's Order-to-Cash process, with specialized agents, integrated tools, and a knowledge base.**
