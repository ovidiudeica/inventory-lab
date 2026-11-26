"""Deterministic calculations; hypotheses are not confirmed root causes."""
from __future__ import annotations

ITEMS = (
    ("SKU-101", "Bearing housing", "A-01", 120, 116, 8.50, "Recent transfer; destination receipt not yet reconciled"),
    ("SKU-102", "Seal kit", "A-02", 80, 80, 4.25, "No exception recorded"),
    ("SKU-103", "Control bracket", "B-01", 45, 49, 24.00, "Recent receipt; duplicate posting check pending"),
    ("SKU-104", "Fastener pack", "B-02", 200, 194, 2.75, "Open picking transaction in sample log"),
    ("SKU-105", "Sensor mount", "C-01", 32, 32, 38.00, "No exception recorded"),
    ("SKU-106", "Cable assembly", "C-02", 12, 8, 65.00, "No recent transaction recorded in sample log"),
)
PROCEDURES = {
    "SOP-01": {"title": "Independent recount", "steps": ["Check SKU and bin labels.", "Recount using a second operator.", "Record quantity, time and evidence."]},
    "SOP-02": {"title": "Transaction reconciliation", "steps": ["Review recent receipts, picks and transfers.", "Compare physical movement against system postings.", "Check open or duplicate transactions."]},
    "SOP-03": {"title": "Escalation and adjustment", "steps": ["Escalate unresolved variances to inventory control.", "Obtain authorised approval before adjusting stock.", "Record the reason and retain the audit trail."]},
}

def stock() -> list[dict]:
    rows = []
    for sku, name, bin_id, system, physical, cost, evidence in ITEMS:
        delta = physical - system
        rows.append(dict(sku=sku, name=name, bin=bin_id, system=system, physical=physical, unit_cost=cost, variance=delta, value_variance=round(delta*cost,2), evidence=evidence, status="Match" if delta == 0 else "Review"))
    return rows

def summary() -> dict:
    rows = stock()
    return dict(skus=len(rows), exceptions=sum(r['variance'] != 0 for r in rows), system_units=sum(r['system'] for r in rows), physical_units=sum(r['physical'] for r in rows), net_variance=sum(r['variance'] for r in rows), absolute_variance=sum(abs(r['variance']) for r in rows), absolute_value=round(sum(abs(r['value_variance']) for r in rows),2), exact_match_pct=round(100*sum(r['variance']==0 for r in rows)/len(rows),1))

def investigate(sku: str) -> dict:
    row = next((r for r in stock() if r['sku']==sku), None)
    if row is None:
        raise KeyError(sku)
    delta = row['variance']
    hypothesis = {"SKU-101":"Unreconciled transfer may explain the shortage.", "SKU-103":"Receipt posting mismatch may explain the surplus.", "SKU-104":"An open pick may explain the shortage.", "SKU-106":"Cause unknown; check recount and transaction history."}.get(sku,"No discrepancy observed.")
    return dict(item=row, hypothesis=hypothesis, conclusion="Unverified hypothesis; do not adjust stock automatically." if delta else "No variance in the sample count.", procedure_ids=["SOP-01","SOP-02","SOP-03"] if delta else ["SOP-01"])

def report(sku: str) -> str:
    case = investigate(sku); r=case['item']
    lines = ["# Inventory investigation — "+sku, "Synthetic data only | Read-only training exercise", "", f"Item: {r['name']} | Bin: {r['bin']}", f"System: {r['system']} | Physical: {r['physical']} | Variance: {r['variance']:+d}", f"Value variance: GBP {r['value_variance']:+.2f}", "", "Evidence: "+r['evidence'], "Hypothesis: "+case['hypothesis'], "Conclusion: "+case['conclusion'], "", "## Recommended procedures"]
    for pid in case['procedure_ids']:
        lines += [f"### {pid} — {PROCEDURES[pid]['title']}"] + [f"- {s}" for s in PROCEDURES[pid]['steps']]
    return '\n'.join(lines)+'\n'
