const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function fetchSummary(hours = 24) {
  const res = await fetch(`${API_BASE}/analytics/summary?hours=${hours}`, { cache: "no-store" });
  return res.json();
}

export async function fetchMessages(limit = 50) {
  const res = await fetch(`${API_BASE}/analytics/messages?limit=${limit}`, { cache: "no-store" });
  return res.json();
}

export async function fetchHourlyVolume(hours = 24) {
  const res = await fetch(`${API_BASE}/analytics/hourly?hours=${hours}`, { cache: "no-store" });
  return res.json();
}

export async function fetchCustomers(tenantId = null) {
  const url = tenantId
    ? `${API_BASE}/analytics/customers?tenant_id=${tenantId}`
    : `${API_BASE}/analytics/customers`;
  const res = await fetch(url, { cache: "no-store" });
  return res.json();
}

export async function fetchTenants() {
  const res = await fetch(`${API_BASE}/admin/tenants`, { cache: "no-store" });
  return res.json();
}

export async function createTenant(data) {
  const res = await fetch(`${API_BASE}/admin/tenants`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function fetchKnowledge(tenantId = null) {
  const url = tenantId
    ? `${API_BASE}/admin/knowledge?tenant_id=${tenantId}`
    : `${API_BASE}/admin/knowledge`;
  const res = await fetch(url, { cache: "no-store" });
  return res.json();
}

export async function addKnowledge(data) {
  const res = await fetch(`${API_BASE}/admin/knowledge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function deleteKnowledge(entryId) {
  const res = await fetch(`${API_BASE}/admin/knowledge/${entryId}`, {
    method: "DELETE",
  });
  return res.json();
}
