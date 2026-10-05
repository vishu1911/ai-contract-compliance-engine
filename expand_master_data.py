from app.database import get_connection


suppliers = [
    ("SUP001", "Apex Industrial Solutions", "Industrial Equipment"),
    ("SUP002", "Vertex Technologies", "Technology"),
    ("SUP003", "Prime Office Systems", "Office Equipment"),
    ("SUP004", "Nova Manufacturing", "Manufacturing"),
    ("SUP005", "TechCore Systems", "Technology"),
    ("SUP006", "Global Industrial Supply", "Industrial Equipment"),
    ("SUP007", "RapidTech Solutions", "Technology"),
    ("SUP008", "Metro Engineering", "Engineering"),
    ("SUP009", "SecureNet Technologies", "Networking"),
    ("SUP011", "Alpha Office Solutions", "Office Equipment"),
    ("SUP012", "NextGen Automation", "Automation"),
    ("SUP013", "PrimeTech Industries", "Technology"),
    ("SUP014", "Precision Engineering Works", "Engineering"),
    ("SUP015", "Vertex Industrial Systems", "Industrial Equipment"),
    ("SUP016", "SmartFab Technologies", "Manufacturing"),
    ("SUP017", "Orbit Electronics", "Electronics"),
    ("SUP018", "DigitalEdge Solutions", "Technology"),
    ("SUP019", "Pioneer Industrial Supply", "Industrial Equipment"),
    ("SUP020", "CloudTech Systems", "Technology"),
    ("SUP021", "Matrix Automation", "Automation"),
]

materials = [
    ("MAT001", "Dell 24-Inch Business Monitor", "IT Equipment", 18000),
    ("MAT002", "HP Business Laptop", "IT Equipment", 65000),
    ("MAT003", "Lenovo ThinkPad Laptop", "IT Equipment", 72000),
    ("MAT005", "Cisco 48-Port Network Switch", "Networking Equipment", 125000),
    ("MAT006", "HP Laser Printer", "Office Equipment", 28000),
    ("MAT007", "Industrial PLC Controller", "Automation", 85000),
    ("MAT008", "Siemens HMI Panel", "Automation", 95000),
    ("MAT009", "Industrial Ethernet Cable", "Networking Equipment", 3200),
    ("MAT010", "Barcode Scanner", "Warehouse Equipment", 14500),
    ("MAT011", "Wireless Access Point", "Networking Equipment", 18500),
    ("MAT012", "UPS 5KVA", "Electrical Equipment", 78000),
    ("MAT013", "Industrial Control Panel", "Automation", 145000),
    ("MAT014", "Temperature Sensor", "Industrial Sensors", 8500),
    ("MAT015", "Pressure Sensor", "Industrial Sensors", 9200),
    ("MAT016", "Servo Motor", "Automation", 55000),
    ("MAT017", "Office Workstation", "Office Equipment", 42000),
    ("MAT018", "Network Firewall", "Networking Equipment", 175000),
    ("MAT019", "Industrial Router", "Networking Equipment", 68000),
    ("MAT020", "RFID Reader", "Warehouse Equipment", 36000),
    ("MAT021", "Industrial Keyboard", "Industrial Equipment", 4500),
]

conn = get_connection()

try:
    with conn.cursor() as cur:

        for supplier_id, supplier_name, category in suppliers:
            cur.execute(
                """
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
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (supplier_id) DO NOTHING;
                """,
                (
                    supplier_id,
                    supplier_name,
                    category,
                    "India",
                    90.00,
                    88.00,
                    92.00,
                    "LOW",
                ),
            )

        for material_id, material_name, category, reference_price in materials:
            cur.execute(
                """
                INSERT INTO materials (
                    material_id,
                    material_name,
                    category,
                    reference_price,
                    currency
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (material_id) DO NOTHING;
                """,
                (
                    material_id,
                    material_name,
                    category,
                    reference_price,
                    "INR",
                ),
            )

    conn.commit()

    print("MASTER DATA EXPANDED SUCCESSFULLY")

finally:
    conn.close()
