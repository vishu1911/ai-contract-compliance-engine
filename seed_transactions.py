from datetime import date, timedelta
from decimal import Decimal

from app.database import get_connection


# ---------------------------------------------------------
# 30 PROCUREMENT SCENARIOS
# ---------------------------------------------------------

scenarios = []

for index in range(1, 31):

    # -----------------------------------------------------
    # IDs
    # -----------------------------------------------------

    contract_id = f"CT{3000 + index}"
    po_id = f"PO{8000 + index}"
    invoice_id = f"INV{10000 + index}"

    # -----------------------------------------------------
    # Supplier / Material
    # -----------------------------------------------------

    supplier_id = f"SUP{((index - 1) % 20) + 1:03d}"
    material_id = f"MAT{((index - 1) % 21) + 1:03d}"

    # -----------------------------------------------------
    # Supplier / material names
    # -----------------------------------------------------

    supplier_names = {
        "SUP001": "Apex Industrial Solutions",
        "SUP002": "Vertex Technologies",
        "SUP003": "Prime Office Systems",
        "SUP004": "Nova Manufacturing",
        "SUP005": "TechCore Systems",
        "SUP006": "Global Industrial Supply",
        "SUP007": "RapidTech Solutions",
        "SUP008": "Metro Engineering",
        "SUP009": "SecureNet Technologies",
        "SUP010": "IndustrialPro",
        "SUP011": "Alpha Office Solutions",
        "SUP012": "NextGen Automation",
        "SUP013": "PrimeTech Industries",
        "SUP014": "Precision Engineering Works",
        "SUP015": "Vertex Industrial Systems",
        "SUP016": "SmartFab Technologies",
        "SUP017": "Orbit Electronics",
        "SUP018": "DigitalEdge Solutions",
        "SUP019": "Pioneer Industrial Supply",
        "SUP020": "CloudTech Systems",
    }

    material_names = {
        "MAT001": "Dell 24-Inch Business Monitor",
        "MAT002": "HP Business Laptop",
        "MAT003": "Lenovo ThinkPad Laptop",
        "MAT004": "Cisco 24-Port Network Switch",
        "MAT005": "Cisco 48-Port Network Switch",
        "MAT006": "HP Laser Printer",
        "MAT007": "Industrial PLC Controller",
        "MAT008": "Siemens HMI Panel",
        "MAT009": "Industrial Ethernet Cable",
        "MAT010": "Barcode Scanner",
        "MAT011": "Wireless Access Point",
        "MAT012": "UPS 5KVA",
        "MAT013": "Industrial Control Panel",
        "MAT014": "Temperature Sensor",
        "MAT015": "Pressure Sensor",
        "MAT016": "Servo Motor",
        "MAT017": "Office Workstation",
        "MAT018": "Network Firewall",
        "MAT019": "Industrial Router",
        "MAT020": "RFID Reader",
        "MAT021": "Industrial Keyboard",
    }

    supplier_name = supplier_names.get(
        supplier_id,
        f"Supplier {supplier_id}"
    )

    material_name = material_names.get(
        material_id,
        f"Material {material_id}"
    )

    # -----------------------------------------------------
    # Reference / Contract Prices
    # -----------------------------------------------------

    reference_prices = {
        "MAT001": 18000,
        "MAT002": 65000,
        "MAT003": 72000,
        "MAT004": 72000,
        "MAT005": 125000,
        "MAT006": 28000,
        "MAT007": 85000,
        "MAT008": 95000,
        "MAT009": 3200,
        "MAT010": 14500,
        "MAT011": 18500,
        "MAT012": 78000,
        "MAT013": 145000,
        "MAT014": 8500,
        "MAT015": 9200,
        "MAT016": 55000,
        "MAT017": 42000,
        "MAT018": 175000,
        "MAT019": 68000,
        "MAT020": 36000,
        "MAT021": 4500,
    }

    contract_price = Decimal(
        str(reference_prices.get(material_id, 50000))
    )

    # -----------------------------------------------------
    # Scenario classification
    #
    # 1-5   = Fully compliant
    # 6-10  = PO price violations
    # 11-15 = Invoice price mismatches
    # 16-20 = Multiple violations
    # 21-25 = Quantity mismatches
    # 26-30 = Severe leakage
    # -----------------------------------------------------

    quantity = Decimal("1")

    po_price = contract_price
    invoice_price = contract_price

    invoice_quantity = quantity

    contract_violation = False
    invoice_mismatch = False
    quantity_mismatch = False

    scenario_type = ""

    # -----------------------------------------------------
    # 1-5: COMPLIANT
    # -----------------------------------------------------

    if 1 <= index <= 5:

        scenario_type = "COMPLIANT"

        po_price = contract_price
        invoice_price = contract_price
        invoice_quantity = quantity

    # -----------------------------------------------------
    # 6-10: PO PRICE VIOLATION
    # -----------------------------------------------------

    elif 6 <= index <= 10:

        scenario_type = "PO_PRICE_VIOLATION"

        po_price = contract_price * Decimal("1.15")
        invoice_price = po_price
        invoice_quantity = quantity

        contract_violation = True

    # -----------------------------------------------------
    # 11-15: INVOICE PRICE MISMATCH
    # -----------------------------------------------------

    elif 11 <= index <= 15:

        scenario_type = "INVOICE_PRICE_MISMATCH"

        po_price = contract_price
        invoice_price = contract_price * Decimal("1.10")
        invoice_quantity = quantity

        invoice_mismatch = True

    # -----------------------------------------------------
    # 16-20: MULTIPLE VIOLATIONS
    # -----------------------------------------------------

    elif 16 <= index <= 20:

        scenario_type = "MULTIPLE_VIOLATIONS"

        po_price = contract_price * Decimal("1.20")
        invoice_price = contract_price * Decimal("1.30")
        invoice_quantity = quantity

        contract_violation = True
        invoice_mismatch = True

    # -----------------------------------------------------
    # 21-25: QUANTITY MISMATCH
    # -----------------------------------------------------

    elif 21 <= index <= 25:

        scenario_type = "QUANTITY_MISMATCH"

        quantity = Decimal("10")

        po_price = contract_price
        invoice_price = contract_price

        invoice_quantity = Decimal("12")

        quantity_mismatch = True

    # -----------------------------------------------------
    # 26-30: SEVERE LEAKAGE
    # -----------------------------------------------------

    else:

        scenario_type = "SEVERE_LEAKAGE"

        po_price = contract_price * Decimal("1.40")
        invoice_price = contract_price * Decimal("1.50")

        quantity = Decimal("5")
        invoice_quantity = quantity

        contract_violation = True
        invoice_mismatch = True

    # -----------------------------------------------------
    # Dates
    # -----------------------------------------------------

    contract_start = date(2026, 1, 1)
    contract_end = date(2026, 12, 31)

    po_date = date(2026, 9, 1) + timedelta(days=index)

    invoice_date = po_date + timedelta(days=5)

    receipt_date = po_date + timedelta(days=3)

    # -----------------------------------------------------
    # Contract
    # -----------------------------------------------------

    scenarios.append(
        {
            "contract_id": contract_id,
            "po_id": po_id,
            "invoice_id": invoice_id,
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "material_id": material_id,
            "material_name": material_name,
            "contract_price": contract_price,
            "po_price": po_price,
            "invoice_price": invoice_price,
            "quantity": quantity,
            "invoice_quantity": invoice_quantity,
            "contract_violation": contract_violation,
            "invoice_mismatch": invoice_mismatch,
            "quantity_mismatch": quantity_mismatch,
            "scenario_type": scenario_type,
            "contract_start": contract_start,
            "contract_end": contract_end,
            "po_date": po_date,
            "invoice_date": invoice_date,
            "receipt_date": receipt_date,
        }
    )


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

conn = get_connection()

try:

    with conn.cursor() as cur:

        for s in scenarios:

            contract_id = s["contract_id"]
            po_id = s["po_id"]
            invoice_id = s["invoice_id"]

            supplier_id = s["supplier_id"]
            material_id = s["material_id"]

            contract_price = s["contract_price"]
            po_price = s["po_price"]
            invoice_price = s["invoice_price"]

            quantity = s["quantity"]
            invoice_quantity = s["invoice_quantity"]

            # -------------------------------------------------
            # CONTRACT
            # -------------------------------------------------

            cur.execute(
                """
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
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                ON CONFLICT (contract_id) DO NOTHING;
                """,
                (
                    contract_id,
                    supplier_id,
                    f"{s['supplier_name']} Supply Agreement",
                    "ANNUAL_SUPPLY",
                    "INR",
                    s["contract_start"],
                    s["contract_end"],
                    "Net 45",
                    "Delivery within 7 business days",
                    "ACTIVE",
                ),
            )

            # -------------------------------------------------
            # CONTRACT ITEM
            # -------------------------------------------------

            cur.execute(
                """
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
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                );
                """,
                (
                    contract_id,
                    material_id,
                    s["material_name"],
                    "ENTERPRISE PROCUREMENT",
                    contract_price,
                    Decimal("0"),
                    Decimal("1"),
                    Decimal("500"),
                    "INR",
                ),
            )

            # -------------------------------------------------
            # PURCHASE ORDER
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
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                );
                """,
                (
                    po_id,
                    contract_id,
                    supplier_id,
                    material_id,
                    quantity,
                    po_price,
                    "INR",
                    s["po_date"],
                    "OPEN",
                ),
            )

            # -------------------------------------------------
            # GOODS RECEIPT
            # -------------------------------------------------

            cur.execute(
                """
                INSERT INTO contract_goods_receipts (
                    po_id,
                    received_quantity,
                    received_date,
                    status
                )
                VALUES (
                    %s, %s, %s, %s
                );
                """,
                (
                    po_id,
                    invoice_quantity,
                    s["receipt_date"],
                    "RECEIVED",
                ),
            )

            # -------------------------------------------------
            # INVOICE
            # -------------------------------------------------

            invoice_total = invoice_price * invoice_quantity

            cur.execute(
                """
                INSERT INTO contract_invoices (
                    invoice_id,
                    po_id,
                    supplier_id,
                    invoice_date,
                    currency,
                    total_amount,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    invoice_id,
                    po_id,
                    supplier_id,
                    s["invoice_date"],
                    "INR",
                    invoice_total,
                    "SUBMITTED",
                ),
            )

            # -------------------------------------------------
            # INVOICE ITEM
            # -------------------------------------------------

            cur.execute(
                """
                INSERT INTO contract_invoice_items (
                    invoice_id,
                    material_id,
                    material_name,
                    quantity,
                    unit_price,
                    currency
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s
                );
                """,
                (
                    invoice_id,
                    material_id,
                    s["material_name"],
                    invoice_quantity,
                    invoice_price,
                    "INR",
                ),
            )

            # -------------------------------------------------
            # PRICE VARIANCE / LEAKAGE
            # -------------------------------------------------

            price_difference = po_price - contract_price

            leakage = max(
                price_difference * quantity,
                Decimal("0")
            )

            # -------------------------------------------------
            # CONTRACT EXCEPTION
            # -------------------------------------------------

            if s["contract_violation"]:

                cur.execute(
                    """
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
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    );
                    """,
                    (
                        po_id,
                        contract_id,
                        supplier_id,
                        material_id,
                        "PRICE_VIOLATION",
                        "HIGH",
                        f"Contract price: INR {contract_price}",
                        f"PO price: INR {po_price}",
                        price_difference,
                        (
                            "Purchase order price exceeds "
                            "the contracted price."
                        ),
                        "OPEN",
                    ),
                )

            # -------------------------------------------------
            # INVOICE EXCEPTION
            # -------------------------------------------------

            if s["invoice_mismatch"]:

                invoice_difference = invoice_price - po_price

                cur.execute(
                    """
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
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    );
                    """,
                    (
                        po_id,
                        contract_id,
                        supplier_id,
                        material_id,
                        "INVOICE_PRICE_MISMATCH",
                        "HIGH",
                        f"PO price: INR {po_price}",
                        f"Invoice price: INR {invoice_price}",
                        invoice_difference,
                        (
                            "Invoice unit price does not "
                            "match the purchase order."
                        ),
                        "OPEN",
                    ),
                )

            # -------------------------------------------------
            # QUANTITY EXCEPTION
            # -------------------------------------------------

            if s["quantity_mismatch"]:

                quantity_difference = (
                    invoice_quantity - quantity
                )

                cur.execute(
                    """
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
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s
                    );
                    """,
                    (
                        po_id,
                        contract_id,
                        supplier_id,
                        material_id,
                        "QUANTITY_MISMATCH",
                        "MEDIUM",
                        f"PO quantity: {quantity}",
                        f"Invoice quantity: {invoice_quantity}",
                        quantity_difference,
                        (
                            "Invoice quantity does not "
                            "match the purchase order quantity."
                        ),
                        "OPEN",
                    ),
                )

            # -------------------------------------------------
            # SPEND LEAKAGE
            # -------------------------------------------------

            if leakage > 0:

                cur.execute(
                    """
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
                        %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    );
                    """,
                    (
                        po_id,
                        contract_id,
                        supplier_id,
                        material_id,
                        contract_price,
                        po_price,
                        quantity,
                        leakage,
                        "CONTRACT_PRICE_VARIANCE",
                    ),
                )

            # -------------------------------------------------
            # COMPLIANCE SCORE
            # -------------------------------------------------

            score = 100

            if s["contract_violation"]:
                score -= 40

            if s["invoice_mismatch"]:
                score -= 30

            if s["quantity_mismatch"]:
                score -= 20

            score = max(score, 0)

            # -------------------------------------------------
            # RISK CATEGORY
            # -------------------------------------------------

            if score >= 80:

                risk = "LOW"
                recommendation = "APPROVE"

            elif score >= 50:

                risk = "MEDIUM"
                recommendation = "REVIEW"

            else:

                risk = "HIGH"
                recommendation = "HOLD_PAYMENT_AND_REVIEW"

            # -------------------------------------------------
            # EXPLANATION
            # -------------------------------------------------

            explanation = (
                f"Scenario: {s['scenario_type']}. "
                f"Contract price is INR {contract_price}. "
                f"PO price is INR {po_price}. "
                f"Invoice price is INR {invoice_price}. "
                f"PO quantity is {quantity}. "
                f"Invoice quantity is {invoice_quantity}."
            )

            # -------------------------------------------------
            # EVIDENCE
            # -------------------------------------------------

            evidence = (
                f"Contract {contract_id}: "
                f"INR {contract_price}; "
                f"PO {po_id}: INR {po_price}; "
                f"Invoice {invoice_id}: INR {invoice_price}; "
                f"PO quantity: {quantity}; "
                f"Invoice quantity: {invoice_quantity}; "
                f"Contract violation: "
                f"{s['contract_violation']}; "
                f"Invoice mismatch: "
                f"{s['invoice_mismatch']}; "
                f"Quantity mismatch: "
                f"{s['quantity_mismatch']}; "
                f"Potential leakage: INR {leakage}."
            )

            # -------------------------------------------------
            # COMPLIANCE ASSESSMENT
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
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                );
                """,
                (
                    po_id,
                    contract_id,
                    supplier_id,
                    material_id,
                    score,
                    risk,
                    recommendation,
                    s["contract_violation"],
                    s["invoice_mismatch"],
                    leakage,
                    explanation,
                    evidence,
                    Decimal("100.00"),
                ),
            )

    # ---------------------------------------------------------
    # COMMIT
    # ---------------------------------------------------------

    conn.commit()

    print()
    print("=" * 60)
    print("30 PROCUREMENT SCENARIOS CREATED SUCCESSFULLY")
    print("=" * 60)
    print()
    print("Contracts : CT3001 - CT3030")
    print("POs       : PO8001 - PO8030")
    print("Invoices  : INV10001 - INV10030")
    print()
    print("Existing PO7001 was NOT modified.")
    print()

except Exception as e:

    conn.rollback()

    print()
    print("ERROR OCCURRED")
    print("=" * 60)
    print(e)
    print()
    print("All changes from this run were rolled back.")
    print("=" * 60)

    raise

finally:

    conn.close()