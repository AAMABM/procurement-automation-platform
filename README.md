# Procurement Automation Platform

An enterprise-grade Procure-to-Pay (P2P) platform designed for organizations undergoing digital transformation and SAP S/4HANA migration. 

This platform automates the entire procurement lifecycle—from requesting goods to sourcing suppliers, issuing purchase orders, matching invoices, and syncing with an ERP system.

## 🚀 Core Features

*   **Identity & Access Control:** JWT authentication, Argon2id password hashing, and granular Role-Based Access Control (RBAC) mirroring SAP authorization objects.
*   **Purchase Requisitions (PR):** State-machine driven approval workflows (Draft → Submitted → Approved).
*   **Sourcing & RFQs:** Create Requests for Quotation, invite vendors, simulate competing quotes, compare pricing, and auto-generate Purchase Orders for the winning bid.
*   **Purchase Orders (PO):** Snapshotting of pricing and vendor assignment.
*   **3-Way Matching & Compliance:** Goods Receipts (GR) and Invoice processing. Automatically flags amount discrepancies as `EXCEPTIONS` to prevent billing fraud.
*   **SAP S/4HANA Integration:** Asynchronous OData payload generation to sync POs with an external ERP, complete with audit logging (simulating SAP WE02).
*   **Analytics Dashboard:** Fiori-style executive dashboard using SQL aggregations to track Total Spend, Exception Rates, and Supplier Performance.

## 💻 Tech Stack

**Backend:**
*   Python 3.12 / FastAPI
*   PostgreSQL / SQLAlchemy (Async) / Alembic
*   Pytest / Pydantic / Structlog

**Frontend:**
*   React / TypeScript / Vite
*   Material UI (MUI)
*   Recharts (Analytics)

**Infrastructure:**
*   Docker / Docker Compose
*   Nginx

## 🏗️ Architecture

The backend follows Clean Architecture principles:
*   **API Layer:** FastAPI routes and Pydantic validation.
*   **Service Layer:** Business logic (State machines, 3-way matching algorithms).
*   **Repository Layer:** Database abstraction (SQLAlchemy).
*   **Models:** ORM entities.

## 🛠️ Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/AAMABM/procurement-automation-platform.git
   cd procurement-automation-platform