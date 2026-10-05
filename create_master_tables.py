from app.database import get_connection

conn = get_connection()

sql = """
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    location VARCHAR(255),
    on_time_delivery_rate DECIMAL(5,2),
    quality_score DECIMAL(5,2),
    compliance_score DECIMAL(5,2),
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materials (
    material_id VARCHAR(50) PRIMARY KEY,
    material_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    reference_price DECIMAL(12,2),
    currency VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

try:
    with conn.cursor() as cur:
        cur.execute(sql)

    conn.commit()
    print("MASTER TABLES CREATED SUCCESSFULLY")

finally:
    conn.close()