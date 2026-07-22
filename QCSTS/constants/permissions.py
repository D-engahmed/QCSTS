class PermissionCodes:
    """
    All permission codes in the CQSTS system.
    These are the only valid permissions that can be
    assigned to a role by the admin.

    Usage:
        from constants.permissions import PermissionCodes
        PermissionCodes.CAN_SUBMIT_RESULT  →  "can_submit_result"
    """

    CAN_CREATE_PRODUCT = "can_create_product"
    CAN_APPROVE_MONOGRAPH = "can_approve_monograph"
    CAN_CREATE_BATCH = "can_create_batch"
    CAN_SUBMIT_RESULT = "can_submit_result"
    CAN_COUNTERSIGN_RESULT = "can_countersign_result"
    CAN_VIEW_AUDIT_TRAIL = "can_view_audit_trail"
    CAN_MANAGE_CHAMBER = "can_manage_chamber"
    CAN_EXPORT_REPORT = "can_export_report"

    ALL = [
        CAN_CREATE_PRODUCT,
        CAN_APPROVE_MONOGRAPH,
        CAN_CREATE_BATCH,
        CAN_SUBMIT_RESULT,
        CAN_COUNTERSIGN_RESULT,
        CAN_VIEW_AUDIT_TRAIL,
        CAN_MANAGE_CHAMBER,
        CAN_EXPORT_REPORT,
    ]
