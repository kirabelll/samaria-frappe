# Samaria ERP (Frappe Framework Version 15)

![Frappe v15 Compatible](https://img.shields.io/badge/Frappe-v15.0%2B-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

**Samaria ERP** is a specialized, production-ready enterprise operations app designed and optimized specifically for **Frappe Framework Version 15** and **ERPNext v15**.

---

## 🌟 Frappe Version 15 Compatibility Matrix

This project is built from the ground up to be 100% compliant with Frappe Version 15 specifications:

| Requirement / Standard | Compatibility Status | Details |
| :--- | :---: | :--- |
| **Python Version** | ✅ Compatible | Supports **Python 3.10, 3.11, and 3.12** (Standard Frappe v15 runtime) |
| **Packaging (PEP 517/621)** | ✅ Compatible | Uses standard `pyproject.toml` with `flit_core` and fallback `setup.py` |
| **Frappe v15 Desk & Workspaces** | ✅ Compatible | Standard block-based Workspace JSON schemas with shortcuts and cards |
| **DocType Engine** | ✅ Compatible | InnoDB MySQL/MariaDB schemas with `naming_rule`, `is_submittable`, and Role Permissions |
| **Document Controllers** | ✅ Compatible | Standard `frappe.model.document.Document` classes and `frappe.whitelist` APIs |
| **Asset Pipeline** | ✅ Compatible | Pure ES6 JavaScript and CSS bundles compatible with `bench build` |

---

## 🏗️ Operational Modules & Features

### 1. 🪨 Aggregate Operations
- **Aggregate Delivery** (`is_submittable`): Manage dispatch and delivery tickets, loaded vs. delivered volume (m³), automatic shortage volume deduction, and driver fee calculations.
- **Aggregate Settlement** (`is_submittable`): Periodic transporter reconciliation batch sheets calculating net payout after shortage and union fee deductions.
- **Transporter Agreements & Rates**: Route-based and material-based transport pricing matrices.

### 2. 🏗️ Cement Operations
- **Cement Purchase**: Procurement contracts tracking quotas, advance payments, and remaining balances per factory.
- **Cement Lifting** (`is_submittable`): Dispatch records linking factory weighbridge, buyer weighbridge, and coupons with automatic stock and balance deductions.
- **Cement Coupon**: Physical coupon custody tracking (`Collected` ➔ `In Custody` ➔ `Handed Over` ➔ `Used` ➔ `Returned`).
- **Cement Weighbridge**: Accurate gross, tare, and net tonnage recording with shortage penalty calculations.

### 3. 💊 Medical Operations
- **Medical Batch**: Lot inventory management with FEFO (First Expiry, First Out) sorting and quarantine flags.
- **Medical Pricing**: 10-tier landed cost buildup formula (FOB + Freight + Insurance + Customs + Inland Transport + Bank + Storage + Handling + Wastage + Overhead) with target profit margin.
- **Medical Request & Store Issue** (`is_submittable`): Customer/Hospital drug orders and store dispensing with batch validation.

### 4. 🚛 Transporter & Fleet Operations
- **Truck & Fleet Master**: Plate numbers, vehicle types, capacity (m³ / Tons), and driver registry.
- **Transport Associations**: Union management, service fee percentages, and bank routing.
- **Transporter Recovery**: Cross-division claim recovery for damages or lost cargo.

### 5. 📊 Executive Dashboard & Reports
- **Samaria Operations Workspace**: Centralized dashboard hub for aggregate, cement, medical, and agreement workflows.
- **Samaria Executive Dashboard Page**: Real-time business intelligence cards, volume trends, factory lifting breakdowns, and recent activity streams.
- **Standard Reports**:
  - *Aggregate Project Dispatch Report*
  - *Cement Project Lifting and Balance Report*
  - *Medical Project Inventory Report*
  - *Project Financial Summary Report*

---

## 🚀 Installation Guide on Frappe Bench (v15)

### Prerequisites
- Frappe Bench v5.20+ with Frappe Version 15 installed.
- Python 3.10, 3.11, or 3.12.

---

### Step 1: Download & Install the App

Navigate to your bench directory and fetch the repository:

```bash
cd ~/frappe-bench

# Fetch app from GitHub repository
bench get-app samaria https://github.com/kirabelll/samaria-frappe.git
```

> **Note:** Providing the explicit app name `samaria` before the URL ensures the folder clones directly to `apps/samaria`.

---

### Step 2: Install App on Your Site

Install the Samaria app on your target Frappe / ERPNext site:

```bash
bench --site <your-site-name> install-app samaria
```
*(Replace `<your-site-name>` with your site name, e.g., `frontend.localhost` or `mysite.local`)*

---

### Step 3: Run Database Migrations

Run database migrations to initialize all DocTypes, Workspaces, and Roles:

```bash
bench --site <your-site-name> migrate
```

---

### Step 4: Build Assets & Restart Bench

Build frontend assets and restart bench background workers:

```bash
bench build --app samaria
bench restart
```

---

## 🔧 Troubleshooting Common Installation Issues

### Issue 1: `OSError: [Errno 39] Directory not empty`
**Cause:** A previous clone attempt failed or an existing folder exists in `apps/samaria` or `apps/samaria-frappe`.

**Fix:**
```bash
# 1. Remove lingering app folders
rm -rf ~/frappe-bench/apps/samaria ~/frappe-bench/apps/samaria-frappe

# 2. Re-run bench get-app with explicit app name
bench get-app samaria https://github.com/kirabelll/samaria-frappe.git
```

---

### Issue 2: DocTypes Not Showing in Workspace
**Cause:** Frappe desk cache needs refreshing after installation.

**Fix:**
```bash
bench --site <your-site-name> clear-cache
bench --site <your-site-name> migrate
```

---

## 🔌 Whitelisted REST APIs (for Custom Frontends & Integrations)

Samaria provides secure, whitelisted Python REST endpoints for integrations:

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `samaria.api.v1.ping` | `GET` | Health check endpoint returning app status and version |
| `samaria.api.v1.get_app_info` | `GET` | App metadata and division list |
| `samaria.api.v1.get_dashboard_data` | `GET` | Consolidated executive metrics and chart datasets |
| `samaria.api.v1.get_aggregate_deliveries` | `GET` | Filterable aggregate dispatches and pricing breakdowns |
| `samaria.api.v1.get_cement_liftings` | `GET` | Cement lifting logs with weighbridge and penalty details |
| `samaria.api.v1.get_cement_purchases` | `GET` | Factory purchase orders with remaining quotas |
| `samaria.api.v1.get_medical_batches` | `GET` | Batch inventory sorted by FEFO (expiry date) |
| `samaria.api.v1.get_medical_requests` | `GET` | Medical order requests and line items |

---

## 👥 Standard User Roles

During migration, the app automatically configures the following roles:
- `Aggregate Manager`
- `Cement Manager`
- `Medical Pharmacist`
- `Medical Druggist`
- `Transporter Coordinator`
- `Weighbridge Operator`
- `System Manager` (Full Access)

---

## 📄 License
This project is licensed under the MIT License - see the [license.txt](file:///d:/samaria/license.txt) file for details.
