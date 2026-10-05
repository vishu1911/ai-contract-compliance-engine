import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg.connect(database_url)

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "ai_contract_compliance"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
    )


def get_compliance_assessment(po_id: str):
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    ca.assessment_id,
                    ca.po_id,
                    ca.contract_id,
                    ca.supplier_id,
                    s.supplier_name,
                    ca.material_id,
                    m.material_name,
                    ca.compliance_score,
                    ca.risk_category,
                    ca.recommendation,
                    ca.contract_violation,
                    ca.invoice_mismatch,
                    ca.potential_leakage,
                    ca.explanation,
                    ca.evidence,
                    ca.confidence,
                    ca.created_at
                FROM compliance_assessments ca
                JOIN suppliers s
                    ON ca.supplier_id = s.supplier_id
                JOIN materials m
                    ON ca.material_id = m.material_id
                WHERE ca.po_id = %s
                ORDER BY ca.created_at DESC
                LIMIT 1;
                """,
                (po_id,),
            )

            row = cur.fetchone()

            if row is None:
                return None

            columns = [
                "assessment_id",
                "po_id",
                "contract_id",
                "supplier_id",
                "supplier_name",
                "material_id",
                "material_name",
                "compliance_score",
                "risk_category",
                "recommendation",
                "contract_violation",
                "invoice_mismatch",
                "potential_leakage",
                "explanation",
                "evidence",
                "confidence",
                "created_at",
            ]

            return dict(zip(columns, row))

    finally:
        conn.close()