from accounts.models import Tenant
from .tenant_utils import get_effective_tenant


def tenant_switcher(request):
    if not request.user.is_authenticated:
        return {
            "active_tenant": None,
            "all_tenants": [],
        }

    if request.user.is_superuser:
        return {
            "active_tenant": get_effective_tenant(request),
            "all_tenants": Tenant.objects.filter(is_active=True).order_by("name"),
        }

    return {
        "active_tenant": request.user.tenant,
        "all_tenants": [],
    }