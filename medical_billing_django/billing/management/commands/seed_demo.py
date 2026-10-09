from datetime import date
from decimal import Decimal
from django.core.management.base import BaseCommand
from billing.models import AccountNote, Claim, EOB, InsurancePayer, Patient


class Command(BaseCommand):
    help = "Create fictional demo insurance payers, patients, claims, EOBs and notes."

    def handle(self, *args, **options):
        payer_names = [
            ("Horizon Gold Plus", "HZ001", "800-555-0101"),
            ("Northstar Health Plan", "NS204", "800-555-0102"),
            ("Evergreen Community Insurance", "EG310", "800-555-0103"),
            ("Blue River Preferred", "BR445", "800-555-0104"),
            ("SummitCare Advantage", "SC550", "800-555-0105"),
        ]
        payers = {}
        for name, code, phone in payer_names:
            payers[name], _ = InsurancePayer.objects.get_or_create(
                name=name, defaults={"payer_code": code, "phone": phone, "active": True}
            )

        patient_specs = [
            ("PT-129-24", "Alex Morgan", date(1984, 8, 14), "MEM-5529413", "100 Main Street, Lexington, KY"),
            ("PT-130-24", "Jamie Taylor", date(1979, 3, 2), "MEM-6631728", "22 Oak Avenue, Dayton, OH"),
            ("PT-131-24", "Casey Jordan", date(1991, 11, 21), "MEM-7718240", "18 River Road, Austin, TX"),
        ]
        patients = {}
        for pid, name, dob, member, address in patient_specs:
            patients[pid], _ = Patient.objects.get_or_create(
                patient_id=pid, defaults={"full_name": name, "date_of_birth": dob, "member_id": member, "address": address}
            )

        claim_specs = [
            ("PT-129-24", "Horizon Gold Plus", date(2025, 1, 28), "99215", "Office / outpatient visit, 40 min", "J20.9, R06.2, R05.9", "318.00", "308.00", "10.00", "Pending", "CO-22: Review coordination of benefits"),
            ("PT-129-24", "Horizon Gold Plus", date(2025, 1, 28), "87636", "SARS-CoV-2 / Influenza A/B panel", "J20.9, R06.2, R05.9", "285.00", "285.00", "0.00", "Denied", "CO-45: Charge exceeds contracted amount"),
            ("PT-129-24", "Northstar Health Plan", date(2025, 1, 28), "87880", "Rapid strep A assay", "J02.9", "20.00", "0.00", "0.00", "Submitted", "CO-18: Possible duplicate claim"),
            ("PT-130-24", "Evergreen Community Insurance", date(2025, 2, 3), "99213", "Office visit, established patient", "R05.9", "145.00", "45.00", "80.00", "Paid", "Payment posted; verify patient responsibility"),
            ("PT-131-24", "Blue River Preferred", date(2025, 2, 5), "93000", "Electrocardiogram, complete", "R07.9", "95.00", "20.00", "50.00", "Rebilled", "Corrected claim submitted"),
        ]
        for index, spec in enumerate(claim_specs, start=1):
            pid, payer_name, svc_date, code, desc, dx, charge, adjustment, payment, status, note = spec
            claim, created = Claim.objects.get_or_create(
                patient=patients[pid], payer=payers[payer_name], service_date=svc_date,
                procedure_code=code, defaults={
                    "provider_name": "RICHARDSON, P.", "procedure_description": desc,
                    "diagnosis_codes": dx, "quantity": 1,
                    "charge_amount": Decimal(charge), "adjustment_amount": Decimal(adjustment),
                    "payment_amount": Decimal(payment), "status": status,
                    "reference_note": note, "batch_number": f"DEMO-{378190 + index}",
                }
            )
            if created:
                EOB.objects.create(
                    claim=claim, eob_number=f"EOB-DEMO-{1000 + index}",
                    payer_claim_number=f"PCN-{55000 + index}",
                    allowed_amount=Decimal(str(max(float(charge) - float(adjustment), 0))),
                    patient_responsibility=Decimal("10.00") if index == 1 else Decimal("0.00"),
                    adjustment_code="CO-45" if "CO-45" in note else ("CO-22" if "CO-22" in note else ""),
                    denial_reason=note if status == "Denied" else "",
                    issued_date=date(2025, 2, 8),
                    document_text=f"DEMO EOB. Claim {claim.id} was processed by {payer_name}. This is fictional sample data.",
                )
        first = patients["PT-129-24"]
        AccountNote.objects.get_or_create(
            patient=first, note="Demo note: claim reviewed; follow up on payer response.",
            defaults={"note_type": "Follow-up", "created_by": "Demo Billing User"},
        )
        self.stdout.write(self.style.SUCCESS("Demo data is ready. All records are fictional."))
