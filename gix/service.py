from decimal import Decimal
from typing import Any

from gix.db import get_connection

STATUSES = ("under_process", "arrived", "problematic")
DEFAULT_TEAM_BUDGET = Decimal("200.00")
DEFAULT_NEW_PURCHASE_STATUS = "under_process"


def _line_total(price_per_item: Decimal, quantity: int) -> Decimal:
    return (price_per_item * quantity).quantize(Decimal("0.01"))


def ensure_team(team_number: int) -> int:
    conn = get_connection(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM teams WHERE team_number = %s",
                (team_number,),
            )
            row = cur.fetchone()
            if row:
                tid = int(row["id"])
                conn.commit()
                return tid
            cur.execute(
                "INSERT INTO teams (team_number, budget_remaining) VALUES (%s, %s)",
                (team_number, DEFAULT_TEAM_BUDGET),
            )
            tid = int(cur.lastrowid)
            conn.commit()
            return tid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_purchase(
    team_number: int,
    cfo_name: str,
    purchase_link: str,
    price_per_item: Decimal,
    quantity: int,
    notes: str | None,
    instructor_approved: bool,
    status: str | None = None,
) -> dict[str, Any]:
    if quantity < 1:
        raise ValueError("Quantity must be at least 1")
    st = status or DEFAULT_NEW_PURCHASE_STATUS
    if st not in STATUSES:
        raise ValueError("Invalid status")

    team_id = ensure_team(team_number)
    total = _line_total(price_per_item, quantity)

    conn = get_connection(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT budget_remaining FROM teams WHERE id = %s FOR UPDATE",
                (team_id,),
            )
            row = cur.fetchone()
            budget = Decimal(str(row["budget_remaining"]))
            if st == "arrived" and budget < total:
                raise ValueError(
                    f"Insufficient budget: need ${total}, team has ${budget} remaining"
                )

            cur.execute(
                """
                INSERT INTO purchases (
                    team_id, cfo_name, purchase_link, price_per_item, quantity,
                    notes, instructor_approved, status, deducted
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    team_id,
                    cfo_name.strip(),
                    purchase_link.strip(),
                    float(price_per_item),
                    quantity,
                    (notes or "").strip() or None,
                    1 if instructor_approved else 0,
                    st,
                    1 if st == "arrived" else 0,
                ),
            )
            pid = int(cur.lastrowid)

            if st == "arrived":
                cur.execute(
                    "UPDATE teams SET budget_remaining = budget_remaining - %s WHERE id = %s",
                    (float(total), team_id),
                )

            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return get_purchase(pid)


def update_purchase_status(purchase_id: int, new_status: str) -> dict[str, Any]:
    if new_status not in STATUSES:
        raise ValueError("Invalid status")

    conn = get_connection(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.team_id, p.price_per_item, p.quantity, p.status, p.deducted
                FROM purchases p WHERE p.id = %s FOR UPDATE
                """,
                (purchase_id,),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError("Purchase not found")

            old_status = row["status"]
            deducted = int(row["deducted"])
            team_id = int(row["team_id"])
            total = _line_total(
                Decimal(str(row["price_per_item"])),
                int(row["quantity"]),
            )

            if old_status == new_status:
                conn.commit()
                return get_purchase(purchase_id)

            if new_status == "arrived" and not deducted:
                cur.execute(
                    "SELECT budget_remaining FROM teams WHERE id = %s FOR UPDATE",
                    (team_id,),
                )
                b = Decimal(str(cur.fetchone()["budget_remaining"]))
                if b < total:
                    raise ValueError(
                        f"Insufficient budget: need ${total}, team has ${b} remaining"
                    )
                cur.execute(
                    "UPDATE teams SET budget_remaining = budget_remaining - %s WHERE id = %s",
                    (float(total), team_id),
                )
                cur.execute(
                    "UPDATE purchases SET status = %s, deducted = 1 WHERE id = %s",
                    (new_status, purchase_id),
                )
            elif old_status == "arrived" and deducted and new_status != "arrived":
                cur.execute(
                    "UPDATE teams SET budget_remaining = budget_remaining + %s WHERE id = %s",
                    (float(total), team_id),
                )
                cur.execute(
                    "UPDATE purchases SET status = %s, deducted = 0 WHERE id = %s",
                    (new_status, purchase_id),
                )
            else:
                cur.execute(
                    "UPDATE purchases SET status = %s WHERE id = %s",
                    (new_status, purchase_id),
                )

            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return get_purchase(purchase_id)


def get_purchase(purchase_id: int) -> dict[str, Any]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.*, t.team_number, t.budget_remaining AS team_budget_now
                FROM purchases p
                JOIN teams t ON t.id = p.team_id
                WHERE p.id = %s
                """,
                (purchase_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        raise ValueError("Purchase not found")
    return _row_to_api(row)


def list_purchases() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.*, t.team_number, t.budget_remaining AS team_budget_now
                FROM purchases p
                JOIN teams t ON t.id = p.team_id
                ORDER BY p.created_at DESC, p.id DESC
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return [_row_to_api(r) for r in rows]


def list_teams() -> list[dict[str, Any]]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, team_number, budget_remaining FROM teams ORDER BY team_number"
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return [
        {
            "id": int(r["id"]),
            "team_number": int(r["team_number"]),
            "budget_remaining": float(r["budget_remaining"]),
        }
        for r in rows
    ]


def _row_to_api(row: dict) -> dict[str, Any]:
    return {
        "id": int(row["id"]),
        "team_number": int(row["team_number"]),
        "team_budget_remaining": float(row["team_budget_now"]),
        "cfo_name": row["cfo_name"],
        "purchase_link": row["purchase_link"],
        "price_per_item": float(row["price_per_item"]),
        "quantity": int(row["quantity"]),
        "notes": row["notes"] or "",
        "instructor_approved": bool(row["instructor_approved"]),
        "status": row["status"],
        "deducted": bool(row["deducted"]),
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
    }
