from django.db import models


class InsurancePayer(models.Model):
    name = models.CharField(max_length=120, unique=True)
    payer_code = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Patient(models.Model):
    patient_id = models.CharField(max_length=30, unique=True)
    full_name = models.CharField(max_length=120)
    date_of_birth = models.DateField(null=True, blank=True)
    member_id = models.CharField(max_length=60, blank=True)
    address = models.CharField(max_length=220, blank=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.patient_id})"


class Claim(models.Model):
    STATUS_CHOICES = [
        ("Submitted", "Submitted"),
        ("Pending", "Pending"),
        ("Denied", "Denied"),
        ("Paid", "Paid"),
        ("Rebilled", "Rebilled"),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="claims")
    payer = models.ForeignKey(InsurancePayer, on_delete=models.PROTECT, related_name="claims")
    provider_name = models.CharField(max_length=120, default="RICHARDSON, P.")
    service_date = models.DateField()
    procedure_code = models.CharField(max_length=20)
    procedure_description = models.CharField(max_length=220)
    diagnosis_codes = models.CharField(max_length=160, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    charge_amount = models.DecimalField(max_digits=10, decimal_places=2)
    adjustment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Submitted")
    reference_note = models.CharField(max_length=300, blank=True)
    batch_number = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-service_date", "procedure_code"]

    @property
    def balance(self):
        return self.charge_amount - self.adjustment_amount - self.payment_amount

    def __str__(self):
        return f"{self.patient.patient_id} - {self.procedure_code}"


class EOB(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="eobs")
    eob_number = models.CharField(max_length=40, unique=True)
    payer_claim_number = models.CharField(max_length=60, blank=True)
    allowed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    patient_responsibility = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    adjustment_code = models.CharField(max_length=30, blank=True)
    denial_reason = models.CharField(max_length=300, blank=True)
    issued_date = models.DateField()
    document_text = models.TextField(blank=True)

    class Meta:
        ordering = ["-issued_date"]

    def __str__(self):
        return self.eob_number


class AccountNote(models.Model):
    NOTE_TYPES = [
        ("Account Note", "Account Note"),
        ("Billing Alert", "Billing Alert"),
        ("Follow-up", "Follow-up"),
        ("Clinical Alert", "Clinical Alert"),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="notes")
    claim = models.ForeignKey(Claim, on_delete=models.SET_NULL, null=True, blank=True, related_name="notes")
    note_type = models.CharField(max_length=30, choices=NOTE_TYPES, default="Account Note")
    note = models.TextField()
    created_by = models.CharField(max_length=120, default="Demo Billing User")
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.note_type} - {self.patient.patient_id}"
