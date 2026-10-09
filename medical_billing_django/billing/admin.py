from django.contrib import admin
from .models import AccountNote, Claim, EOB, InsurancePayer, Patient

@admin.register(InsurancePayer)
class InsurancePayerAdmin(admin.ModelAdmin):
    list_display = ("name", "payer_code", "phone", "active")
    search_fields = ("name", "payer_code")
    list_filter = ("active",)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "full_name", "member_id")
    search_fields = ("patient_id", "full_name", "member_id")

class EOBInline(admin.TabularInline):
    model = EOB
    extra = 0

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "payer", "procedure_code", "service_date", "charge_amount", "status")
    list_filter = ("status", "payer", "service_date")
    search_fields = ("patient__full_name", "patient__patient_id", "procedure_code", "batch_number")
    inlines = [EOBInline]

@admin.register(AccountNote)
class AccountNoteAdmin(admin.ModelAdmin):
    list_display = ("patient", "claim", "note_type", "created_by", "created_at", "active")
    list_filter = ("note_type", "active")
    search_fields = ("patient__full_name", "note")
