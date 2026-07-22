from django.db import models
from core.models import BaseModel, ActiveManager


class Monograph(BaseModel):
    """
    Defines the testing specification for a product.
    A monograph must be approved before any batch can be created
    against it. This is Rule R-01 in our business rules.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("inactive", "Inactive"),
    ]

    name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    effective_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    approved_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_monographs",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "products_monograph"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} v{self.version}"

    def is_approved(self):
        return self.status == "approved"


class MonographTest(BaseModel):
    """
    A single test defined inside a monograph.
    e.g. Assay, pH, Dissolution, Moisture Content.

    Each MonographTest defines:
    - what to test (name)
    - how to test it (method)
    - what result is acceptable (specification)
    """

    monograph = models.ForeignKey(Monograph, on_delete=models.CASCADE, related_name="tests")
    name = models.CharField(max_length=255, help_text="e.g. Assay, pH, Dissolution")
    method = models.CharField(max_length=255, help_text="e.g. USP <711>, HPLC Method A")
    specification = models.CharField(
        max_length=500, help_text="e.g. 98.0% - 102.0%, NLT 75% in 30 min"
    )
    unit = models.CharField(max_length=50, blank=True, help_text="e.g. %, mg, pH units")
    sequence = models.PositiveIntegerField(
        default=1, help_text="Display order of this test in the monograph"
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "products_monograph_test"
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.monograph.name} — {self.name}"


class Product(BaseModel):
    """
    A drug product registered in the system.
    Must be linked to an approved monograph before
    any batch can be created.
    """

    DOSAGE_FORM_CHOICES = [
        ("tablet", "Tablet"),
        ("capsule", "Capsule"),
        ("syrup", "Syrup"),
        ("injection", "Injection"),
        ("cream", "Cream"),
        ("ointment", "Ointment"),
        ("gel", "Gel"),
        ("suppository", "Suppository"),
        ("suspension", "Suspension"),
        ("solution", "Solution"),
    ]

    name = models.CharField(max_length=255)
    strength = models.CharField(max_length=100, help_text="e.g. 500 mg, 250 mg/5 ml")
    dosage_form = models.CharField(max_length=50, choices=DOSAGE_FORM_CHOICES)
    description = models.TextField(blank=True)
    monograph = models.ForeignKey(
        Monograph, on_delete=models.PROTECT, related_name="products", null=True, blank=True
    )

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "products_product"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} {self.strength}"
