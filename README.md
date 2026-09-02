# Samaria Frappe App (Version-16)

Modern custom Frappe App and Module setup built for **Frappe Framework Version-16**.

---

## 📁 Repository Structure

```text
samaria/
├── .gitignore
├── license.txt
├── pyproject.toml              # Modern PEP 621 packaging (Frappe v15/v16 standard)
├── README.md
└── samaria/                    # App Python package
    ├── __init__.py             # Version metadata
    ├── hooks.py                # Frappe v16 hooks & event registry
    ├── modules.txt             # Registered modules (Samaria)
    ├── patches.txt             # Schema migration patches
    ├── api/                    # Whitelisted REST endpoints
    │   ├── __init__.py
    │   └── v1.py
    ├── tasks/                  # Background worker routines & cron jobs
    │   ├── __init__.py
    │   └── cron.py
    ├── samaria/                # 'Samaria' Module Directory
    │   ├── __init__.py
    │   ├── doctype/            # DocTypes (Models & Controllers)
    │   │   ├── __init__.py
    │   │   └── samaria_setting/
    │   │       ├── __init__.py
    │   │       ├── samaria_setting.json
    │   │       ├── samaria_setting.py
    │   │       ├── samaria_setting.js
    │   │       └── test_samaria_setting.py
    │   └── workspace/          # Desk Workspace definitions
    │       ├── __init__.py
    │       └── samaria/
    │           └── samaria.json
    ├── public/                 # Client assets (bundled in Desk)
    │   ├── js/
    │   │   └── samaria.bundle.js
    │   └── css/
    │       └── samaria.bundle.css
    ├── templates/              # Jinja templates
    └── www/                    # Public portal web pages
```

---

## 🚀 Installation & Setup in Bench

### 1. Link / Get the App into your Bench
If developing locally in your bench environment:
```bash
cd /path/to/frappe-bench

# If linking local folder:
bench get-app samaria /d/projects/samaria

# Or from Git repo:
# bench get-app https://github.com/samaria/samaria.git
```

### 2. Install App to your Site
```bash
bench --site [your-site-name] install-app samaria
```

### 3. Run Migrations & Build Assets
```bash
bench --site [your-site-name] migrate
bench build --app samaria
```

### 4. Verify Installation
Start bench:
```bash
bench start
```
- Open Desk and search for **Samaria Workspace** or **Samaria Setting**.
- Call the test ping API:
  `GET /api/method/samaria.api.v1.ping`

---

## 🛠 Features Included in this Setup

1. **PEP 621 Build System**: Uses `pyproject.toml` with `flit_core` compatible with modern pip & Frappe v16.
2. **Standard Single DocType**: `Samaria Setting` with validation logic and interactive Desk action button.
3. **Desk Workspace**: Ready-to-use modern Frappe v16 workspace definition (`Samaria`).
4. **Hooks Configuration**: Pre-configured for document events, scheduler cron jobs (`hourly`, `daily`), asset bundling, and APIs.
5. **Background Workers**: Modular background cron runners under `samaria.tasks.cron`.
6. **Whitelisted REST API**: Clean endpoint structure in `samaria.api.v1`.

---

## 📜 License
MIT
