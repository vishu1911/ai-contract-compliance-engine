from app.database import get_connection

conn = get_connection()

sql = """
CREATE TABLE IF NOT EXISTS contracts (
    contract_id VARCHAR(50) PRIMARY KEY,
    supplier_id VARCHAR(50) NOT NULL,
    contract_name VARCHAR(255) NOT NULL,
    contract_type VARCHAR(100),
    currency VARCHAR(10) NOT NULL,
    effective_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    payment_terms VARCHAR(100),
    delivery_terms VARCHAR(255),
    status VARCHAR(30),
    document_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE IF NOT EXISTS contract_items (
    contract_item_id SERIAL PRIMARY KEY,
    contract_id VARCHAR(50) NOT NULL,
    material_id VARCHAR(50) NOT NULL,
    material_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    contract_price DECIMAL(12,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    min_quantity DECIMAL(12,2),
    max_quantity DECIMAL(12,2),
    currency VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);

CREATE TABLE IF NOT EXISTS contract_purchase_orders (
    po_id VARCHAR(50) PRIMARY KEY,
    contract_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    material_id VARCHAR(50) NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    po_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);

CREATE TABLE IF NOT EXISTS contract_exceptions (
    exception_id SERIAL PRIMARY KEY,
    po_id VARCHAR(50) NOT NULL,
    contract_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    material_id VARCHAR(50) NOT NULL,
    exception_type VARCHAR(100) NOT NULL,
    severity VARCHAR(30) NOT NULL,
    expected_value TEXT,
    actual_value TEXT,
    variance_amount DECIMAL(14,2),
    description TEXT,
    status VARCHAR(50) DEFAULT 'OPEN',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES contract_purchase_orders(po_id),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);

CREATE TABLE IF NOT EXISTS spend_leakage (
    leakage_id SERIAL PRIMARY KEY,
    po_id VARCHAR(50) NOT NULL,
    contract_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    material_id VARCHAR(50) NOT NULL,
    contracted_price DECIMAL(12,2) NOT NULL,
    actual_price DECIMAL(12,2) NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    leakage_amount DECIMAL(14,2) NOT NULL,
    leakage_type VARCHAR(100) NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES contract_purchase_orders(po_id),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);

CREATE TABLE IF NOT EXISTS contract_goods_receipts (
    receipt_id SERIAL PRIMARY KEY,
    po_id VARCHAR(50) NOT NULL,
    received_quantity DECIMAL(12,2) NOT NULL,
    received_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES contract_purchase_orders(po_id)
);

CREATE TABLE IF NOT EXISTS contract_invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    po_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    currency VARCHAR(10) NOT NULL,
    total_amount DECIMAL(14,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES contract_purchase_orders(po_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

CREATE TABLE IF NOT EXISTS contract_invoice_items (
    invoice_item_id SERIAL PRIMARY KEY,
    invoice_id VARCHAR(50) NOT NULL,
    material_id VARCHAR(50) NOT NULL,
    material_name VARCHAR(255) NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES contract_invoices(invoice_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);

CREATE TABLE IF NOT EXISTS compliance_assessments (
    assessment_id SERIAL PRIMARY KEY,
    po_id VARCHAR(50) NOT NULL,
    contract_id VARCHAR(50) NOT NULL,
    supplier_id VARCHAR(50) NOT NULL,
    material_id VARCHAR(50) NOT NULL,
    compliance_score DECIMAL(5,2),
    risk_category VARCHAR(30),
    recommendation VARCHAR(100),
    contract_violation BOOLEAN DEFAULT FALSE,
    invoice_mismatch BOOLEAN DEFAULT FALSE,
    potential_leakage DECIMAL(14,2) DEFAULT 0,
    explanation TEXT,
    evidence TEXT,
    confidence DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES contract_purchase_orders(po_id),
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (material_id) REFERENCES materials(material_id)
);
"""

try:
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("PROJECT 2 SCHEMA CREATED SUCCESSFULLY")
finally:
    conn.close()