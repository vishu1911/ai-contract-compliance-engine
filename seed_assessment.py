from app.database import get_connection

conn = get_connection()

sql = """
INSERT INTO contract_exceptions (
    po_id,
    contract_id,
    supplier_id,
    material_id,
    exception_type,
    severity,
    expected_value,
    actual_value,
    variance_amount,
    description,
    status
)
VALUES (
    'PO7001',
    'CT-1045',
    'SUP010',
    'MAT004',
    'PRICE_VIOLATION',
    'HIGH',
    'Contract price INR 72000',
    'PO price INR 90000',
    18000.00,
    'Purchase order price exceeds contracted price by 25 percent.',
    'OPEN'
);

INSERT INTO spend_leakage (
    po_id,
    contract_id,
    supplier_id,
    material_id,
    contracted_price,
    actual_price,
    quantity,
    leakage_amount,
    leakage_type
)
VALUES (
    'PO7001',
    'CT-1045',
    'SUP010',
    'MAT004',
    72000.00,
    90000.00,
    1,
    18000.00,
    'CONTRACT_PRICE_VARIANCE'
);

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
    'PO7001',
    'CT-1045',
    'SUP010',
    'MAT004',
    30.00,
    'HIGH',
    'HOLD_PAYMENT_AND_REVIEW',
    TRUE,
    TRUE,
    18000.00,
    'PO price exceeds contract price and invoice price exceeds PO price.',
    'Contract price INR 72000; PO price INR 90000; invoice price INR 105000; quantity 1; contract violation TRUE; invoice mismatch TRUE; potential leakage INR 18000.',
    100.00
);
"""

try:
    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()
    print("COMPLIANCE ASSESSMENT SEEDED SUCCESSFULLY")

finally:
    conn.close()