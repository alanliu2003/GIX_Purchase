# GIX team purchase tracker

Web app for teams to **submit purchases** (student view) and for a **coordinator** to review them, set status (**Under process** / **Arrived** / **Problematic**), and track per-team **budget** (default starting balance $200). Data is stored in **MySQL**.

Two UIs are included:

| Interface | How to run | Default URL |
|-----------|------------|-------------|
| **JavaScript + FastAPI** | `uvicorn` or Docker service `web` | http://localhost:8000 |
| **Streamlit** | `streamlit run` or Docker service `streamlit` | http://localhost:8501 |

Budget is deducted when a purchase first moves to **Arrived** (not when it is still **Under process**).

---

## Option A — Run with Docker (easiest for third parties)

You get MySQL and both apps in one step. No local MySQL install required.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with **Docker Compose** (v2 plugin or `docker-compose`).

### Steps

1. **Clone or copy** this repository and open a terminal in the project root (the folder that contains `docker-compose.yml`).

2. **Create a file named `.env`** in that same folder with:

   ```env
   MYSQL_ROOT_PASSWORD=choose_a_strong_password_you_invent
   ```

   This value is **only for the MySQL server inside Docker**. You choose it; it does not need to match any MySQL on your computer.

3. **Start everything:**

   ```bash
   docker compose up --build -d
   ```

4. **Open a browser**

   - Main web app: **http://localhost:8000** (or `http://<server-ip>:8000` from another machine on the network).
   - Streamlit: **http://localhost:8501**

5. **Stop** (keeps database data):

   ```bash
   docker compose down
   ```

   To **delete all data** as well:

   ```bash
   docker compose down -v
   ```

More detail (HTTPS, VPS firewall, troubleshooting): see **[DOCKER.md](DOCKER.md)**.

---

## Option B — Run on your machine (Python + MySQL)

Use this if you already run MySQL locally (e.g. MySQL Workbench).

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **MySQL 8** (or compatible) with a user that can create the database

### Steps

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   ```

   **Windows (PowerShell):** `.\.venv\Scripts\Activate.ps1`  
   **macOS/Linux:** `source .venv/bin/activate`

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment.** Copy `.env.example` to `.env` and edit:

   ```env
   MYSQL_HOST=127.0.0.1
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=gix_purchases
   ```

   `MYSQL_PASSWORD` must match the password for `MYSQL_USER` on **your** MySQL server (the one Workbench uses).

4. **Create tables** (once per database):

   ```bash
   python init_db.py
   ```

   You should see `Schema applied OK.`

5. **Run the JavaScript web app:**

   ```bash
   python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Open **http://localhost:8000**

6. **Run Streamlit** (optional; use a **second** terminal, same venv):

   ```bash
   streamlit run streamlit_app.py
   ```

   Open the URL Streamlit prints (often **http://localhost:8501**).

---

## Using the app

- **Student:** Submit team number, CFO name, purchase link, price per item, quantity, notes, and instructor approval.
- **Coordinator:** See all submissions and team budgets; change status. **Arrived** triggers budget deduction for that line (if not already deducted).

---

## Security note

This project does **not** ship with logins. Anyone who can open the URL can use both student and coordinator flows. For production or the public internet, use HTTPS, a reverse proxy, VPN, IP restrictions, or add authentication.

---

## Project layout (short)

| Path | Role |
|------|------|
| `api/main.py` | FastAPI + REST + static frontend |
| `frontend/` | HTML / CSS / JavaScript UI |
| `streamlit_app.py`, `pages/` | Streamlit student/coordinator pages |
| `gix/` | Config, DB access, business logic |
| `database/schema.sql` | MySQL table definitions |
| `init_db.py` | Applies `schema.sql` |
| `docker-compose.yml`, `Dockerfile` | Container deployment |

---

## License / course use

Use and modify as needed for your course or team. If you deploy publicly, read **[DOCKER.md](DOCKER.md)** for HTTPS and firewall tips.
