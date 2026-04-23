from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Tenant
from processing.models import Department


DEFAULT_DEPARTMENTS = [
    "Geschäftsführung",
    "Verwaltung",
    "Buchhaltung",
    "Personal",
    "IT",
    "Compliance",
    "Vertrieb",
    "Marketing",
    "Einkauf",
    "Kundenservice",
]


def ensure_default_departments_for_tenant(tenant):
    if tenant is None:
        return

    existing_names = set(
        Department.objects.filter(tenant=tenant).values_list("name", flat=True)
    )

    missing_names = [
        name for name in DEFAULT_DEPARTMENTS
        if name not in existing_names
    ]

    Department.objects.bulk_create(
        [
            Department(tenant=tenant, name=name)
            for name in missing_names
        ]
    )


@receiver(post_save, sender=Tenant)
def create_default_departments_for_new_tenant(sender, instance, created, **kwargs):
    if created:
        ensure_default_departments_for_tenant(instance)