"""
Canonical permission catalog.

Why this exists:
    Permissions are a *shared language* between the backend enforcement
    layer and the frontend UI (which will hide actions the user can't
    perform). Centralizing codes prevents drift between teams.

Format:  "<resource>:<action>"
    Mirrors AWS IAM / Kubernetes RBAC / SAP authorization object naming.

SAP S/4HANA relevance:
    Each code maps conceptually to an SAP authorization object. For example,
    `purchasing_orders:approve` ~ M_BEST_BSA with ACTVT='02' and a value
    threshold. Storing them as strings gives us the flexibility to introduce
    threshold-value restrictions in a later phase via ABAC.
"""
from enum import StrEnum


class PermissionCode(StrEnum):
    # --- Identity & access ---
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    USERS_DELETE = "users:delete"
    ROLES_READ = "roles:read"
    ROLES_WRITE = "roles:write"

    # --- Reserved for future phases (declared now to stabilize the API) ---
    VENDORS_READ = "vendors:read"
    VENDORS_WRITE = "vendors:write"
    REQUISITIONS_READ = "requisitions:read"
    REQUISITIONS_WRITE = "requisitions:write"
    REQUISITIONS_APPROVE = "requisitions:approve"
    PURCHASE_ORDERS_READ = "purchase_orders:read"
    PURCHASE_ORDERS_WRITE = "purchase_orders:write"
    PURCHASE_ORDERS_APPROVE = "purchase_orders:approve"
    INVOICES_READ = "invoices:read"
    INVOICES_WRITE = "invoices:write"
    REPORTS_VIEW = "reports:view"
    AUDIT_READ = "audit:read"


# System roles — the minimum set required to bootstrap the platform.
SYSTEM_ROLES: dict[str, dict] = {
    "admin": {
        "description": "Full platform administrator.",
        "permissions": [p.value for p in PermissionCode],
    },
    "procurement_manager": {
        "description": "Manages vendors, requisitions, and purchase orders.",
        "permissions": [
            PermissionCode.VENDORS_READ.value,
            PermissionCode.VENDORS_WRITE.value,
            PermissionCode.REQUISITIONS_READ.value,
            PermissionCode.REQUISITIONS_WRITE.value,
            PermissionCode.REQUISITIONS_APPROVE.value,
            PermissionCode.PURCHASE_ORDERS_READ.value,
            PermissionCode.PURCHASE_ORDERS_WRITE.value,
            PermissionCode.PURCHASE_ORDERS_APPROVE.value,
            PermissionCode.INVOICES_READ.value,
            PermissionCode.REPORTS_VIEW.value,
        ],
    },
    "buyer": {
        "description": "Creates requisitions and purchase orders.",
        "permissions": [
            PermissionCode.VENDORS_READ.value,
            PermissionCode.REQUISITIONS_READ.value,
            PermissionCode.REQUISITIONS_WRITE.value,
            PermissionCode.PURCHASE_ORDERS_READ.value,
            PermissionCode.PURCHASE_ORDERS_WRITE.value,
            PermissionCode.INVOICES_READ.value,
        ],
    },
    "viewer": {
        "description": "Read-only auditor / business partner.",
        "permissions": [
            PermissionCode.REQUISITIONS_READ.value,
            PermissionCode.PURCHASE_ORDERS_READ.value,
            PermissionCode.INVOICES_READ.value,
            PermissionCode.REPORTS_VIEW.value,
        ],
    },
}