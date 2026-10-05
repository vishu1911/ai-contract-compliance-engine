from app.database import get_compliance_assessment
from app.gemini_service import analyze_compliance


def run_compliance_analysis(po_id: str):
    assessment = get_compliance_assessment(po_id)

    if assessment is None:
        return {
            "success": False,
            "message": f"No compliance assessment found for {po_id}."
        }

    evidence = f"""
PO ID: {assessment["po_id"]}
Contract ID: {assessment["contract_id"]}
Supplier: {assessment["supplier_name"]}
Material: {assessment["material_name"]}

Compliance Score: {assessment["compliance_score"]}
Risk Category: {assessment["risk_category"]}
Recommendation: {assessment["recommendation"]}

Contract Violation: {assessment["contract_violation"]}
Invoice Mismatch: {assessment["invoice_mismatch"]}
Potential Leakage: INR {assessment["potential_leakage"]}

Explanation:
{assessment["explanation"]}

Evidence:
{assessment["evidence"]}
"""

    ai_analysis = analyze_compliance(evidence)

    return {
        "success": True,
        "po_id": po_id,
        "deterministic_assessment": assessment,
        "ai_analysis": ai_analysis
    }