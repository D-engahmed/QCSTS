"""
Tenant-scoped serializer fields.

Why this exists
----------------
TestResultSerializer scopes its FK querysets to the active organization by
hand, in __init__. That pattern works, but it is opt-in — a developer has to
remember it on every serializer that references a tenant-owned model. Nobody
did, on four other serializers, and each one is a live cross-tenant write:

    ChangeBatchLocationSerializer.batch    -> Batch.objects.all()
    SamplePullSerializer.batch/.test_point -> {Batch,TestPoint}.objects.all()
    ProductSerializer.monograph            -> Monograph.objects.all()
    BatchSerializer.product                -> Product.objects.all()

Any authenticated user of ANY organization could submit another organization's
record ID in one of these fields and it would validate — because
PrimaryKeyRelatedField's default queryset has no idea a request, let alone a
tenant, exists. That is a write-path IDOR: the read side was scoped
(core.views.TenantScopedAPIView), the write side referencing existing records
was not.

This mirrors core/views.py: make the safe behaviour structural, not
remembered.
"""

from rest_framework import serializers


class TenantScopedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """
    A PrimaryKeyRelatedField restricted to ``context["request"].organization``.

    The restriction is applied in ``get_queryset()``, which DRF calls only
    during ``to_internal_value`` (i.e. when parsing WRITE input) — never during
    ``to_representation`` (READ output). That means:

      * Serializing an already-scoped queryset for a GET response works with
        no context, exactly like before.
      * Calling ``.is_valid()`` on WRITE input without
        ``context={"request": request}`` raises immediately, loudly, and
        BEFORE anything is saved. It does not fall back to an unscoped
        queryset — a silent fallback here is exactly the bug this class
        exists to close.
    """

    def get_queryset(self):
        base_queryset = super().get_queryset()
        request = self.context.get("request")
        if request is None or getattr(request, "organization", None) is None:
            raise RuntimeError(
                f"{self.__class__.__name__} for field '{self.field_name}' was "
                "validated with no organization in serializer context. Pass "
                "context={'request': request} when instantiating this "
                "serializer for writes — never let a tenant-owned reference "
                "field validate against an unscoped queryset."
            )
        return base_queryset.filter(organization=request.organization)


class TenantScopedModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that swaps every writable FK field targeting a
    tenant-owned model for a ``TenantScopedPrimaryKeyRelatedField``.

    This closes the auto-generated-field version of the bug: a plain
    ``fields = ["batch", ...]`` on a ModelSerializer makes DRF generate a bare,
    unscoped ``PrimaryKeyRelatedField`` for `batch` with nothing visibly wrong
    on review — the vulnerability is an absence, not a line of code. Because
    the swap happens for every instantiation (read or write), a write attempt
    with no request context fails loudly via ``get_queryset()`` above, rather
    than silently validating against every tenant's data.
    """

    # Models that carry `organization` and must never be referenced across
    # tenants. Extend this set as new tenant-owned models are added — the
    # structural test in core/tests/test_serializer_tenant_scoping.py fails
    # the build if a new organization-owned model's FK field is left off it.
    TENANT_OWNED_MODELS = {
        "Batch", "Product", "Monograph", "MonographTest",
        "TestPoint", "TestResult", "SamplePull", "Site",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in list(self.fields.items()):
            if type(field) is not serializers.PrimaryKeyRelatedField:
                continue  # already customised (e.g. explicitly scoped) — leave it
            if field.read_only or field.queryset is None:
                continue
            target_model = field.queryset.model.__name__
            if target_model not in self.TENANT_OWNED_MODELS:
                continue
            # Assigning into self.fields (a BindingDict) calls .bind() on the
            # new field automatically, which is where it picks up .context via
            # its parent chain — DRF fields never take context in __init__.
            self.fields[name] = TenantScopedPrimaryKeyRelatedField(
                queryset=field.queryset,
                required=field.required,
                allow_null=field.allow_null,
                source=field.source if field.source != name else None,
            )
