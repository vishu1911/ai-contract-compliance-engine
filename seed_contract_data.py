from app.database import get_connection

conn = get_connection()

sql = """
INSERT INTO contracts (
    contract_id,
    supplier_id,
    contract_name,
    contract_type,
    currency,
    effective_date,
    expiry_date,
    payment_terms,
    delivery_terms,
    status
)
VALUES (
    'CT-1045',
    'SUP010',
    'IndustrialPro Network Equipment Supply Agreement',
    'ANNUAL_SUPPLY',
    'INR',
    '2026-01-01',
    '2026-12-31',
    'Net 45',
    'Delivery within 7 business days',
    'ACTIVE'
)
ON CONFLICT (contract_id) DO NOTHING;

INSERT INTO contract_items (
    contract_id,
    material_id,
    material_name,
    category,
    contract_price,
    discount_percent,
    min_quantity,
    max_quantity,
    currency
)
VALUES (
    'CT-1045',
    'MAT004',
    'Cisco 24-Port Network Switch',
    'Networking Equipment',
    72000.00,
    8.00,
    1,
    500,
    'INR'
);
"""

try:
    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()
    print("CONTRACT DATA SEEDED SUCCESSFULLY")

finally:
    conn.close()
