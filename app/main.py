from decimal import Decimal
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.database import get_connection
from app.langgraph_workflow import compliance_graph


app = FastAPI(
    title="AI Contract Compliance & Spend Intelligence Engine",
    description="GenAI-powered contract compliance and procurement analysis",
    version="1.0.0",
)


BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "templates" / "index.html"


# =========================================================
# MODELS
# =========================================================

class PurchaseOrderCreate(BaseModel):
    contract_id: str
    material_id: str
    quantity: float
    unit_price: float


# =========================================================
# HOME
# =========================================================

@app.get("/", response_class=HTMLResponse)
def root():
    return HTML_FILE.read_text(encoding="utf-8")


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# =========================================================
# CONTRACTS
# =========================================================

@app.get("/contracts")
def get_contracts():

    conn = get_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.contract_id,
                    c.supplier_id,
                    s.supplier_name,
                    c.contract_name,
                    c.contract_type,
                    c.currency,
                    c.effective_date,
                    c.expiry_date,
                    c.payment_terms,
                    c.delivery_terms,
                    c.status,
                    ci.material_id,
                    ci.material_name,
                    ci.category,
                    ci.contract_price,
                    ci.discount_percent,
                    ci.min_quantity,
                    ci.max_quantity
                FROM contracts c
                JOIN suppliers s
                    ON c.supplier_id = s.supplier_id
                LEFT JOIN contract_items ci
                    ON c.contract_id = ci.contract_id
                WHERE c.status = 'ACTIVE'
                ORDER BY c.contract_id;
                """
            )

            rows = cur.fetchall()

            contracts = []

            for row in rows:

                contracts.append(
                    {
                        "contract_id": row[0],
                        "supplier_id": row[1],
                        "supplier_name": row[2],
                        "contract_name": row[3],
                        "contract_type": row[4],
                        "currency": row[5],
                        "effective_date": str(row[6]),
                        "expiry_date": str(row[7]),
                        "payment_terms": row[8],
                        "delivery_terms": row[9],
                        "status": row[10],
                        "material_id": row[11],
                        "material_name": row[12],
                        "category": row[13],
                        "contract_price": float(row[14]),
                        "discount_percent": float(row[15] or 0),
                        "min_quantity": float(row[16] or 0),
                        "max_quantity": float(row[17] or 0),
                    }
                )

            return {
                "success": True,
                "count": len(contracts),
                "contracts": contracts,
            }

    finally:
        conn.close()


# =========================================================
# CREATE PURCHASE ORDER
# =========================================================

@app.post("/purchase-orders")
def create_purchase_order(po: PurchaseOrderCreate):

    if po.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero."
        )

    if po.unit_price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Unit price must be greater than zero."
        )

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            # -------------------------------------------------
            # GET CONTRACT + MATERIAL
            # -------------------------------------------------

            cur.execute(
                """
                SELECT
                    c.contract_id,
                    c.supplier_id,
                    s.supplier_name,
                    ci.material_id,
                    ci.material_name,
                    ci.contract_price,
                    ci.min_quantity,
                    ci.max_quantity,
                    c.currency
                FROM contracts c
                JOIN suppliers s
                    ON c.supplier_id = s.supplier_id
                JOIN contract_items ci
                    ON c.contract_id = ci.contract_id
                WHERE c.contract_id = %s
                  AND ci.material_id = %s
                  AND c.status = 'ACTIVE'
                LIMIT 1;
                """,
                (
                    po.contract_id,
                    po.material_id,
                )
            )

            contract = cur.fetchone()

            if contract is None:
                raise HTTPException(
                    status_code=404,
                    detail="Contract or material not found."
                )

            (
                contract_id,
                supplier_id,
                supplier_name,
                material_id,
                material_name,
                contract_price,
                min_quantity,
                max_quantity,
                currency,
            ) = contract

            # -------------------------------------------------
            # GENERATE PO ID
            # -------------------------------------------------

            cur.execute(
                """
                SELECT COALESCE(
                    MAX(
                        CAST(
                            SUBSTRING(po_id FROM 3)
                            AS INTEGER
                        )
                    ),
                    8000
                )
                FROM contract_purchase_orders
                WHERE po_id LIKE 'PO%';
                """
            )

            max_po_number = cur.fetchone()[0]

            new_po_id = f"PO{max_po_number + 1}"

            # -------------------------------------------------
            # CREATE PO
            # -------------------------------------------------

            cur.execute(
                """
                INSERT INTO contract_purchase_orders (
                    po_id,
                    contract_id,
                    supplier_id,
                    material_id,
                    quantity,
                    unit_price,
                    currency,
                    po_date,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    CURRENT_DATE,
                    %s
                );
                """,
                (
                    new_po_id,
                    contract_id,
                    supplier_id,
                    material_id,
                    Decimal(str(po.quantity)),
                    Decimal(str(po.unit_price)),
                    currency,
                    "OPEN",
                )
            )

            # -------------------------------------------------
            # CONTRACT COMPLIANCE CHECK
            # -------------------------------------------------

            contract_price_decimal = Decimal(str(contract_price))
            po_price_decimal = Decimal(str(po.unit_price))
            quantity_decimal = Decimal(str(po.quantity))

            price_difference = (
                po_price_decimal - contract_price_decimal
            )

            price_variance_percent = Decimal("0")

            if contract_price_decimal > 0:

                price_variance_percent = (
                    price_difference
                    / contract_price_decimal
                    * Decimal("100")
                )

            contract_violation = (
                po_price_decimal > contract_price_decimal
            )

            potential_leakage = Decimal("0")

            if contract_violation:
                potential_leakage = (
                    price_difference * quantity_decimal
                )

            # -------------------------------------------------
            # COMPLIANCE SCORE
            # -------------------------------------------------

            score = 100

            if contract_violation:
                score -= 40

            # Quantity outside contract range
            quantity_violation = False

            if min_quantity is not None:
                if quantity_decimal < Decimal(str(min_quantity)):
                    quantity_violation = True

            if max_quantity is not None:
                if quantity_decimal > Decimal(str(max_quantity)):
                    quantity_violation = True

            if quantity_violation:
                score -= 20

            score = max(score, 0)

            # -------------------------------------------------
            # RISK
            # -------------------------------------------------

            if score >= 80:

                risk_category = "LOW"
                recommendation = "APPROVE"

            elif score >= 50:

                risk_category = "MEDIUM"
                recommendation = "REVIEW"

            else:

                risk_category = "HIGH"
                recommendation = "HOLD_PAYMENT_AND_REVIEW"

            # -------------------------------------------------
            # EXPLANATION
            # -------------------------------------------------

            explanation = (
                f"Purchase order {new_po_id} was created against "
                f"contract {contract_id}. "
                f"Contract price is INR {contract_price_decimal}. "
                f"PO unit price is INR {po_price_decimal}. "
                f"Price variance is "
                f"{price_variance_percent.quantize(Decimal('0.01'))}%. "
                f"Contract violation: {contract_violation}."
            )

            if quantity_violation:

                explanation += (
                    f" Quantity {quantity_decimal} is outside "
                    f"the contractual range of "
                    f"{min_quantity} to {max_quantity}."
                )

            evidence = (
                f"Contract ID: {contract_id}\n"
                f"Supplier: {supplier_name}\n"
                f"Material: {material_name}\n"
                f"Contract Price: INR {contract_price_decimal}\n"
                f"PO Price: INR {po_price_decimal}\n"
                f"Quantity: {quantity_decimal}\n"
                f"Price Variance: "
                f"{price_variance_percent.quantize(Decimal('0.01'))}%\n"
                f"Contract Violation: {contract_violation}\n"
                f"Quantity Violation: {quantity_violation}\n"
                f"Potential Leakage: INR {potential_leakage}"
            )

            # -------------------------------------------------
            # SAVE COMPLIANCE ASSESSMENT
            # -------------------------------------------------

            cur.execute(
                """
                INSERT INTO compliance_assessments (
                    po_id,
                    contract_id,
                    supplier_id,
                    material_id,
                    compliance_score,
                    risk_category,
                    recommendation,
                    contract_violation,
                    invoice_mismatch,
                    potential_leakage,
                    explanation,
                    evidence,
                    confidence
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                );
                """,
                (
                    new_po_id,
                    contract_id,
                    supplier_id,
                    material_id,
                    score,
                    risk_category,
                    recommendation,
                    contract_violation,
                    False,
                    potential_leakage,
                    explanation,
                    evidence,
                    Decimal("100.00"),
                )
            )

            conn.commit()

            return {
                "success": True,
                "po_id": new_po_id,
                "contract_id": contract_id,
                "supplier_id": supplier_id,
                "supplier_name": supplier_name,
                "material_id": material_id,
                "material_name": material_name,
                "quantity": float(quantity_decimal),
                "contract_price": float(contract_price_decimal),
                "po_price": float(po_price_decimal),
                "price_variance_percent": float(
                    price_variance_percent
                ),
                "compliance_score": score,
                "risk_category": risk_category,
                "recommendation": recommendation,
                "contract_violation": contract_violation,
                "quantity_violation": quantity_violation,
                "potential_leakage": float(
                    potential_leakage
                ),
                "explanation": explanation,
                "evidence": evidence,
            }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:

        conn.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        conn.close()


# =========================================================
# AI ANALYSIS
# =========================================================

@app.get("/analyze/{po_id}")
def analyze_po(po_id: str):

    try:

        result = compliance_graph.invoke(
            {
                "po_id": po_id
            }
        )

        return {
            "success": True,
            "po_id": po_id,
            "assessment": result["assessment"],
            "ai_analysis": result["ai_analysis"],
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@app.get("/dashboard-summary")
def dashboard_summary():

    conn = get_connection()

    try:

        with conn.cursor() as cur:

            # Active contracts
            cur.execute(
                """
                SELECT COUNT(*)
                FROM contracts
                WHERE status = 'ACTIVE';
                """
            )

            active_contracts = cur.fetchone()[0]

            # Purchase orders
            cur.execute(
                """
                SELECT COUNT(*)
                FROM contract_purchase_orders;
                """
            )

            total_pos = cur.fetchone()[0]

            # High-risk
            cur.execute(
                """
                SELECT COUNT(*)
                FROM compliance_assessments
                WHERE risk_category = 'HIGH';
                """
            )

            high_risk = cur.fetchone()[0]

            # Potential leakage
            cur.execute(
                """
                SELECT COALESCE(
                    SUM(leakage_amount),
                    0
                )
                FROM spend_leakage;
                """
            )

            potential_leakage = cur.fetchone()[0]

            # Invoices
            cur.execute(
                """
                SELECT COUNT(*)
                FROM contract_invoices;
                """
            )

            total_invoices = cur.fetchone()[0]

            # Exceptions
            cur.execute(
                """
                SELECT COUNT(*)
                FROM contract_exceptions
                WHERE status = 'OPEN';
                """
            )

            open_exceptions = cur.fetchone()[0]

            # Risk distribution
            cur.execute(
                """
                SELECT
                    risk_category,
                    COUNT(*)
                FROM compliance_assessments
                GROUP BY risk_category
                ORDER BY risk_category;
                """
            )

            risk_rows = cur.fetchall()

            risk_distribution = {
                row[0]: row[1]
                for row in risk_rows
            }

            return {
                "active_contracts": active_contracts,
                "total_purchase_orders": total_pos,
                "total_invoices": total_invoices,
                "high_risk": high_risk,
                "open_exceptions": open_exceptions,
                "potential_leakage": float(
                    potential_leakage
                ),
                "risk_distribution": risk_distribution,
            }

    finally:
        conn.close()