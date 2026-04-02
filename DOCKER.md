# Docker deployment

Runs **MySQL 8**, the **FastAPI + JavaScript** app (port **8000**), and **Streamlit** (port **8501**) so anyone can use the product over the network.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac) or Docker Engine + Compose (Linux).

## Quick start

1. In the project root, create a `.env` file **used only by Compose** (you can keep a different `.env` for local Python—Compose loads `.env` from the same folder as `docker-compose.yml`).

   ```env
   MYSQL_ROOT_PASSWORD=your_strong_password_here
   ```

2. Build and start:

   ```bash
   docker compose up --build -d
   ```

3. Open in a browser (replace with your server’s public or LAN IP):

   - **JavaScript UI:** `http://YOUR_IP:8000`
   - **Streamlit UI:** `http://YOUR_IP:8501`

4. Check logs:

   ```bash
   docker compose logs -f web
   ```

5. Stop:

   ```bash
   docker compose down
   ```

Data persists in the **`mysql_data`** Docker volume until you run `docker compose down -v`.

## Deploy on a VPS (internet)

1. SSH into the server, install Docker and Compose plugin.
2. Clone this repo (or copy files), `cd` into the project.
3. Create `.env` with `MYSQL_ROOT_PASSWORD` as above.
4. `docker compose up --build -d`
5. In the cloud provider’s **firewall / security group**, allow inbound **TCP 8000** and **8501** (or only **80/443** if you use a reverse proxy below).

**Security:** This app has **no login**. Only expose it on networks you trust, or put it behind **VPN**, **HTTP basic auth**, or **IP allowlisting**. For a class demo, restrict firewall rules to campus IPs if possible.

## HTTPS and a domain (recommended for public URLs)

Do **not** send passwords over plain HTTP on the public internet. Put a reverse proxy in front:

- **Caddy** (automatic HTTPS): install Caddy on the host, point DNS `A`/`AAAA` to the server, use a `Caddyfile` that reverse-proxies `https://your.domain` → `127.0.0.1:8000` (and another site or path for Streamlit on `8501` if needed).
- **nginx** with **Let’s Encrypt** (certbot) works similarly.

The containers can keep listening on `8000`/`8501` on localhost; only the proxy faces the world on **443**.

## Troubleshooting

- **MySQL healthcheck fails:** Ensure `MYSQL_ROOT_PASSWORD` in `.env` has no stray quotes/spaces. Try `docker compose logs mysql`.
- **Streamlit “image not found”:** Run `docker compose up --build` so the `web` service builds `gix-purchases-app:latest` first.
- **Schema errors:** Entrypoints run `init_db` automatically; re-run with `docker compose up` after fixing MySQL.

## Optional: change ports

In `.env`:

```env
WEB_PORT=8080
STREAMLIT_PORT=8502
```

Then `docker compose up -d` again.
