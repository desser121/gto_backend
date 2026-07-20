from django.db import models
from django.contrib.auth.models import User

ROLE_CHOICES = [
    ('root', 'Суперадмин'),
    ('admin', 'Администратор'),
    ('editor', 'Редактор'),
    ('viewer', 'Наблюдатель'),
]

ROLE_PERMISSIONS = {
    'root': ['manage_users', 'create_list', 'delete_list', 'edit_list', 'view_list', 'export_federal', 'save_list'],
    'admin': ['create_list', 'delete_list', 'edit_list', 'view_list', 'export_federal', 'save_list'],
    'editor': ['create_list', 'edit_list', 'view_list', 'export_federal', 'save_list'],
    'viewer': ['view_list', 'export_federal'],
}

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    @property
    def permissions(self):
        return ROLE_PERMISSIONS.get(self.role, ROLE_PERMISSIONS['viewer'])
