from app.database import get_connection

conn = get_connection()

sql = """
INSERT INTO suppliers (
    supplier_id,
    supplier_name,
    category,
    location,
    on_time_delivery_rate,
    quality_score,
    compliance_score,
    risk_level
)
VALUES (
    'SUP010',
    'IndustrialPro',
    'Industrial Equipment',
    'Pune, Maharashtra',
    92.00,
    88.00,
    76.00,
    'HIGH'
)
ON CONFLICT (supplier_id) DO NOTHING;

INSERT INTO materials (
    material_id,
    material_name,
    category,
    reference_price,
    currency
)
VALUES (
    'MAT004',
    'Cisco 24-Port Network Switch',
    'Networking Equipment',
    72000.00,
    'INR'
)
ON CONFLICT (material_id) DO NOTHING;
"""

try:
    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()
    print("MASTER DATA SEEDED SUCCESSFULLY")

finally:
    conn.close()