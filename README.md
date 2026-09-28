# Samaria (Version-15)

**Samaria ERP Specialized Operations App for Frappe Framework Version 15.**

This app implements the specialized enterprise domains for Samaria ERP:
1. **Aggregate Operations**: Quarry-to-client dispatches, volume measurements, shortage deductions, proof verification, and transporter batch settlements.
2. **Cement Operations**: Factory procurement orders, coupon registry and driver handovers, weighbridge lifting records, buyer shortage penalty calculations, and factory balances.
3. **Medical Operations**: FEFO (First Expiry, First Out) batch management, comprehensive landed-cost buildup pricing formulas, customer prescription/orders, and store dispensing issues.
4. **Transporter Operations**: Association management, transporter registry, fleet/truck master, dynamic category & item rate agreements, claim recoveries, and automated payment sheets.

---

## 📁 Modules & DocTypes

### 1. Aggregate Module
- **Aggregate Delivery** (`is_submittable`): Records material dispatches, loaded vs delivered volumes, calculates shortages, applies shortage deductions against transport fees, and attaches telegram/signed receipts.
- **Aggregate Settlement** (`is_submittable`): Transporter periodic settlement sheet aggregating deliveries, applying association fees and recovery deductions to compute net payable.
- **Aggregate Settlement Item** (Child Table): Delivery line item within settlement sheets.

### 2. Cement Module
- **Factory**: Cement/Aggregate plant and supplier source registry with weighbridge and coupon settings.
- **Cement Purchase**: Procurement contracts with factory tracking purchased tonnage, unit price, advance payments, and remaining balance.
- **Cement Coupon**: Coupon tracking lifecycle (`Collected` ➔ `In Custody` ➔ `Handed Over` ➔ `Used` ➔ `Returned`).
- **Cement Lifting** (`is_submittable`): Offloading record linking factory weighbridge, buyer weighbridge, coupon, and truck, with automated balance deduction on submit.
- **Cement Weighbridge**: Gross, tare, and net weighbridge ticket capture with photo proof and operator verification.
- **Cement Penalty**: Penalty assessment and claim recovery for shortage, damage, or delivery delays.

### 3. Medical Module
- **Medical Batch**: Batch tracking with expiry dates, stock quantities, cost prices, and automated expired status handling.
- **Medical Pricing**: 10-tier cost buildup (FOB price + Freight + Insurance + Customs + Inland Transport + Bank + Storage + Handling + Wastage + Overheads) + Target margin to calculate recommended and approved selling prices.
- **Medical Request**: Customer/Hospital order request with prioritization.
- **Medical Request Item** (Child Table): Medicine line items with batch preferences.
- **Medical Store Issue** (`is_submittable`): Dispatch and store release note validating stock availability and batch expiry, deducting inventory on submit.
- **Medical Store Issue Item** (Child Table): Batch allocation line items.

### 4. Transporter Module
- **Transport Association**: Association master with default service charge deduction rates and bank info.
- **Transporter**: Transporter entity with withholding tax rules, association links, and payment details.
- **Truck**: Fleet master with plate number, category (Sinotruk, Dump Truck, Trailer, etc.), capacity, and driver info.
- **Transporter Agreement**: Rate contract supporting route pricing, item rates, shortage penalty rates, and category capacity matrix.
- **Transporter Agreement Item** (Child Table): Material transport rate and shortage value.
- **Transporter Pricing** (Child Table): Truck category capacity pricing.
- **Transporter Recovery**: Claim and shortage recovery tracking across aggregate and cement divisions.
- **Truck Payment** (`is_submittable`): Payment batch sheet calculating gross fee, shortage deduction, association charge, and recovery deductions.

---

## 🚀 Installation & Setup on Frappe Bench (v15)

### 1. Clone or copy `samaria` into your bench `apps` folder:
```bash
cd /path/to/frappe-bench/apps
# If copying locally:
cp -r /path/to/samariaERP/samaria ./samaria
```

### 2. Install the app in your bench environment:
```bash
bench pip install -e apps/samaria
```

### 3. Install the app onto your site:
```bash
bench --site [your-site-name] install-app samaria
```

### 4. Run database migrations:
```bash
bench --site [your-site-name] migrate
```

### 5. Build assets:
```bash
bench build --app samaria
bench restart
```

---

## 🔌 REST APIs & Frontend Integration

Samaria includes whitelisted Python API endpoints for Next.js / frontend integration:

### Aggregate API (`samaria.api.aggregate`)
- `get_unsettled_deliveries(transporter, from_date, to_date)`: Returns all unsettled dispatches for a transporter.
- `get_aggregate_analytics()`: Summary metrics (total dispatches, loaded volume, delivered volume, shortages, paid transport).

### Cement API (`samaria.api.cement`)
- `get_factory_balances()`: Factory-wise purchased vs remaining quota.
- `get_cement_analytics()`: Analytics for cement liftings, active coupons, and shortage penalties.

### Medical API (`samaria.api.medical`)
- `get_fefo_batches(item_code, required_qty)`: Auto-selects batches sorted by FEFO (earliest expiry first).
- `create_store_issue_from_request(request_id)`: Generates a Store Issue pre-allocated with FEFO batches.
- `get_expiring_batches_report(days_threshold=90)`: List batches expiring in upcoming days.

### Transporter API (`samaria.api.transporter`)
- `get_active_rate(transporter, product_type, item_code)`: Looks up agreed transport rate and shortage penalty rate.
- `get_transporter_recovery_balance(transporter)`: Calculates outstanding claims and recoveries.

---

## 👥 Roles & Permissions Included
- **Aggregate Manager**
- **Cement Manager**
- **Medical Pharmacist**
- **Medical Druggist**
- **Transporter Coordinator**
- **Weighbridge Operator**
- **System Manager**
