from .models import AccessRule

def has_permission(user, element_name, action, obj=None):
    if not user or not user.is_active:
        return False

    # Админ имеет полный доступ
    if user.role and user.role.name == 'admin':
        return True

    try:
        rule = AccessRule.objects.get(role=user.role, element__name=element_name)
    except AccessRule.DoesNotExist:
        return False

    if action == 'read':
        if obj and obj.owner != user and not rule.can_read_all:
            return False
        return rule.can_read
    elif action == 'create':
        return rule.can_create
    elif action == 'update':
        if obj and obj.owner != user and not rule.can_update_all:
            return False
        return rule.can_update
    elif action == 'delete':
        if obj and obj.owner != user and not rule.can_delete_all:
            return False
        return rule.can_delete
    return False