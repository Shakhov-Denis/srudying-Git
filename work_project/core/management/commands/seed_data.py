from django.core.management.base import BaseCommand
from core.models import Role, BusinessElement, AccessRule, User

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Роли
        admin_role, _ = Role.objects.get_or_create(name='admin')
        manager_role, _ = Role.objects.get_or_create(name='manager')
        user_role, _ = Role.objects.get_or_create(name='user')
        guest_role, _ = Role.objects.get_or_create(name='guest')

        # Бизнес-элементы
        elements = ['users', 'products', 'orders', 'access_rules']
        for elem in elements:
            BusinessElement.objects.get_or_create(name=elem)

        # Правила для админа (полный доступ)
        admin_role.access_rules.all().delete()
        for elem in BusinessElement.objects.all():
            AccessRule.objects.create(
                role=admin_role,
                element=elem,
                can_read=True, can_read_all=True,
                can_create=True,
                can_update=True, can_update_all=True,
                can_delete=True, can_delete_all=True
            )

        # Правила для user
        user_elem = BusinessElement.objects.get(name='products')
        AccessRule.objects.get_or_create(
            role=user_role, element=user_elem,
            defaults={'can_read': True, 'can_create': True}
        )

        # Создаём тестового админа
        if not User.objects.filter(email='admin@example.com').exists():
            admin = User.objects.create(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                role=admin_role
            )
            admin.set_password('adminpass')
            admin.save()

        self.stdout.write('Test data created')