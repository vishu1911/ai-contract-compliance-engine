from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.database import get_compliance_assessment
from app.gemini_service import analyze_compliance


class ComplianceState(TypedDict, total=False):
    po_id: str
    assessment: dict
    evidence: str
    ai_analysis: str


def fetch_compliance_data(state: ComplianceState):
    assessment = get_compliance_assessment(state["po_id"])

    if assessment is None:
        raise ValueError(
            f"No compliance assessment found for {state['po_id']}."
        )

    return {
        "assessment": assessment
    }


def build_evidence(state: ComplianceState):
    assessment = state["assessment"]

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

    return {
        "evidence": evidence
    }


def generate_ai_analysis(state: ComplianceState):
    ai_analysis = analyze_compliance(state["evidence"])

    return {
        "ai_analysis": ai_analysis
    }


workflow = StateGraph(ComplianceState)

workflow.add_node("fetch_compliance_data", fetch_compliance_data)
workflow.add_node("build_evidence", build_evidence)
workflow.add_node("generate_ai_analysis", generate_ai_analysis)

workflow.add_edge(START, "fetch_compliance_data")
workflow.add_edge("fetch_compliance_data", "build_evidence")
workflow.add_edge("build_evidence", "generate_ai_analysis")
workflow.add_edge("generate_ai_analysis", END)

compliance_graph = workflow.compile()