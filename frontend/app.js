const API = "";

function $(sel) {
  return document.querySelector(sel);
}

function showMsg(el, text, ok) {
  el.textContent = text || "";
  el.classList.remove("ok", "error");
  if (text) el.classList.add(ok ? "ok" : "error");
}

async function fetchJSON(path, options = {}) {
  const res = await fetch(API + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function switchView(name) {
  $("#view-student").classList.toggle("hidden", name !== "student");
  $("#view-coordinator").classList.toggle("hidden", name !== "coordinator");
  document.querySelectorAll(".tab").forEach((btn) => {
    const on = btn.dataset.view === name;
    btn.classList.toggle("active", on);
    btn.setAttribute("aria-selected", on ? "true" : "false");
  });
  if (name === "coordinator") loadCoordinator();
}

function money(n) {
  const x = Number(n);
  return Number.isFinite(x) ? x.toFixed(2) : "—";
}

function lineTotal(p) {
  return Number(p.price_per_item) * Number(p.quantity);
}

async function loadCoordinator() {
  const msg = $("#coord-msg");
  showMsg(msg, "");
  try {
    const [purchases, teams] = await Promise.all([
      fetchJSON("/api/purchases"),
      fetchJSON("/api/teams"),
    ]);

    const budgets = $("#budgets");
    budgets.innerHTML = teams
      .map(
        (t) =>
          `<span class="budget-chip">Team ${t.team_number}: <span>$${money(
            t.budget_remaining
          )}</span></span>`
      )
      .join("");

    const tbody = $("#tbody-purchases");
    tbody.innerHTML = purchases
      .map((p) => {
        const total = lineTotal(p);
        const opts = ["under_process", "arrived", "problematic"]
          .map(
            (s) =>
              `<option value="${s}" ${p.status === s ? "selected" : ""}>${labelStatus(
                s
              )}</option>`
          )
          .join("");
        return `<tr data-id="${p.id}">
          <td>${p.id}</td>
          <td>${p.team_number}</td>
          <td>${escapeHtml(p.cfo_name)}</td>
          <td><a href="${encodeURI(p.purchase_link)}" target="_blank" rel="noopener">link</a></td>
          <td>${money(p.price_per_item)}</td>
          <td>${p.quantity}</td>
          <td>${money(total)}</td>
          <td>${escapeHtml(p.notes || "")}</td>
          <td>${p.instructor_approved ? "Yes" : "No"}</td>
          <td><select class="status-select" aria-label="Status">${opts}</select></td>
          <td>${money(p.team_budget_remaining)}</td>
          <td>${formatDate(p.created_at)}</td>
        </tr>`;
      })
      .join("");

    tbody.querySelectorAll("select.status-select").forEach((sel) => {
      sel.addEventListener("change", onStatusChange);
    });
  } catch (e) {
    showMsg(msg, e.message, false);
  }
}

function labelStatus(s) {
  if (s === "under_process") return "Under process";
  if (s === "arrived") return "Arrived";
  if (s === "problematic") return "Problematic";
  return s;
}

function formatDate(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

function escapeHtml(s) {
  const div = document.createElement("div");
  div.textContent = s;
  return div.innerHTML;
}

async function onStatusChange(ev) {
  const sel = ev.target;
  const tr = sel.closest("tr");
  const id = tr && tr.dataset.id;
  if (!id) return;
  const status = sel.value;
  const msg = $("#coord-msg");
  showMsg(msg, "Saving…", true);
  try {
    await fetchJSON(`/api/purchases/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    showMsg(msg, "Updated.", true);
    await loadCoordinator();
  } catch (e) {
    showMsg(msg, e.message, false);
    await loadCoordinator();
  }
}

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => switchView(btn.dataset.view));
});

$("#form-purchase").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const form = ev.target;
  const fd = new FormData(form);
  const body = {
    team_number: Number(fd.get("team_number")),
    cfo_name: String(fd.get("cfo_name") || "").trim(),
    purchase_link: String(fd.get("purchase_link") || "").trim(),
    price_per_item: String(fd.get("price_per_item")),
    quantity: Number(fd.get("quantity")),
    notes: String(fd.get("notes") || ""),
    instructor_approved: fd.get("instructor_approved") === "on",
  };
  const msg = $("#student-msg");
  showMsg(msg, "");
  try {
    await fetchJSON("/api/purchases", {
      method: "POST",
      body: JSON.stringify(body),
    });
    showMsg(msg, "Purchase recorded.", true);
    form.reset();
  } catch (e) {
    showMsg(msg, e.message, false);
  }
});

$("#btn-refresh").addEventListener("click", () => loadCoordinator());
