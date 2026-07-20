from .models import AuditLog


def log_action(user, action, description='', target_name=''):
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        target_name=target_name,
    )
