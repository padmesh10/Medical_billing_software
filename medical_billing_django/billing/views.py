import json
from decimal import Decimal
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from .models import AccountNote, Claim, EOB, InsurancePayer, Patient


def dashboard(request):
    patients = Patient.objects.all()
    payers = InsurancePayer.objects.filter(active=True)
    claims = Claim.objects.select_related("patient", "payer").prefetch_related("eobs")
    notes = AccountNote.objects.select_related("patient", "claim")[:12]
    totals = claims.aggregate(charges=Sum("charge_amount"), adjustments=Sum("adjustment_amount"), payments=Sum("payment_amount"))
    totals = {key: (value or Decimal("0.00")) for key, value in totals.items()}
    totals["balance"] = totals["charges"] - totals["adjustments"] - totals["payments"]
    selected_patient = request.GET.get("patient", "")
    selected_payer = request.GET.get("payer", "")
    if selected_patient:
        claims = claims.filter(patient_id=selected_patient)
    if selected_payer:
        claims = claims.filter(payer_id=selected_payer)
    return render(request, "billing/dashboard.html", {
        "patients": patients, "payers": payers, "claims": claims,
        "notes": notes, "totals": totals,
        "selected_patient": selected_patient, "selected_payer": selected_payer,
    })


@require_GET
def claim_detail(request, claim_id):
    claim = get_object_or_404(Claim.objects.select_related("patient", "payer"), pk=claim_id)
    return JsonResponse({
        "id": claim.id,
        "patient": claim.patient.full_name,
        "patient_id": claim.patient.patient_id,
        "payer": claim.payer.name,
        "member_id": claim.patient.member_id,
        "provider": claim.provider_name,
        "service_date": claim.service_date.isoformat(),
        "procedure_code": claim.procedure_code,
        "procedure_description": claim.procedure_description,
        "diagnosis_codes": claim.diagnosis_codes,
        "quantity": claim.quantity,
        "charge_amount": str(claim.charge_amount),
        "adjustment_amount": str(claim.adjustment_amount),
        "payment_amount": str(claim.payment_amount),
        "balance": str(claim.balance),
        "status": claim.status,
        "batch_number": claim.batch_number,
        "reference_note": claim.reference_note,
        "eobs": [{"id": e.id, "number": e.eob_number} for e in claim.eobs.all()],
    })


@require_GET
def eob_detail(request, eob_id):
    eob = get_object_or_404(EOB.objects.select_related("claim", "claim__patient", "claim__payer"), pk=eob_id)
    return JsonResponse({
        "id": eob.id,
        "eob_number": eob.eob_number,
        "payer_claim_number": eob.payer_claim_number,
        "patient": eob.claim.patient.full_name,
        "payer": eob.claim.payer.name,
        "procedure_code": eob.claim.procedure_code,
        "issued_date": eob.issued_date.isoformat(),
        "charge_amount": str(eob.claim.charge_amount),
        "allowed_amount": str(eob.allowed_amount),
        "patient_responsibility": str(eob.patient_responsibility),
        "adjustment_code": eob.adjustment_code,
        "denial_reason": eob.denial_reason,
        "document_text": eob.document_text,
    })


@require_POST
def add_note(request):
    patient_id = request.POST.get("patient_id")
    claim_id = request.POST.get("claim_id") or None
    note_type = request.POST.get("note_type", "Account Note")
    note_text = request.POST.get("note", "").strip()
    if not note_text:
        messages.error(request, "Please enter a note before saving.")
        return redirect("billing:dashboard")
    patient = get_object_or_404(Patient, pk=patient_id)
    claim = get_object_or_404(Claim, pk=claim_id) if claim_id else None
    if claim and claim.patient_id != patient.id:
        messages.error(request, "Selected claim does not belong to this patient.")
        return redirect("billing:dashboard")
    valid_types = {choice[0] for choice in AccountNote.NOTE_TYPES}
    if note_type not in valid_types:
        note_type = "Account Note"
    AccountNote.objects.create(patient=patient, claim=claim, note_type=note_type, note=note_text)
    messages.success(request, "Account note saved.")
    return redirect("billing:dashboard")


@require_POST
def update_claim_status(request, claim_id):
    claim = get_object_or_404(Claim, pk=claim_id)
    status = request.POST.get("status")
    allowed = {choice[0] for choice in Claim.STATUS_CHOICES}
    if status not in allowed:
        return JsonResponse({"ok": False, "error": "Invalid status"}, status=400)
    claim.status = status
    claim.save(update_fields=["status"])
    return JsonResponse({"ok": True, "status": claim.status})
