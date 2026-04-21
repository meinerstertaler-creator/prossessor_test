from accounts.models import Tenant


SESSION_KEY_ACTIVE_TENANT_ID = "active_tenant_id"


def get_effective_tenant(request):
    """
    Gibt den aktiven Mandanten zurück:
    - bei normalen Benutzern immer request.user.tenant
    - bei Superusern den in der Session gewählten Tenant
    - None = alle Mandanten
    """
    user = request.user

    if not user.is_authenticated:
        return None

    if not user.is_superuser:
        return user.tenant

    tenant_id = request.session.get(SESSION_KEY_ACTIVE_TENANT_ID)

    if not tenant_id:
        return None

    try:
        return Tenant.objects.get(pk=tenant_id)
    except Tenant.DoesNotExist:
        request.session.pop(SESSION_KEY_ACTIVE_TENANT_ID, None)
        return None


def get_effective_tenant_queryset_filter(request):
    tenant = get_effective_tenant(request)
    if tenant is None:
        return None
    return tenant