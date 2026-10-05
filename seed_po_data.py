from app.database import get_connection

conn = get_connection()

sql = """
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
    'PO7001',
    'CT-1045',
    'SUP010',
    'MAT004',
    1,
    90000.00,
    'INR',
    '2026-09-15',
    'OPEN'
)
ON CONFLICT (po_id) DO NOTHING;
"""

try:
    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()
    print("PO DATA SEEDED SUCCESSFULLY")

finally:
    conn.close()