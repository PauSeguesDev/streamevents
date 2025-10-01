from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from faker import Faker
import unidecode

# Obtenim el model d'usuari actiu a Django (pot ser User personalitzat)
User = get_user_model()

# Inicialitzem Faker amb configuració per espanyol
faker = Faker('es_ES')

# Creem la classe de comanda
class Command(BaseCommand):
    # Descripció de la comanda que es mostra quan fem 'python manage.py help'
    help = '🌱 Crea usuaris de prova per al desenvolupament'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Nombre d\'usuaris a crear'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            default=False,
            help='Elimina usuaris existents (excepte superusuaris)'
        )
        parser.add_argument(
            '--with-follows',
            action='store_true',
            default=False,
            help='Crea relacions de seguiment aleatòries'
        )

    # Funció principal que s'executa quan cridem la comanda
    def handle(self, *args, **options):
        # Si s'ha passat --clear, eliminem els usuaris existents
        if options['clear']:
            self.stdout.write('🗑️  Eliminant usuaris existents...')
            count = 0
            # Excloem els superusuaris per no eliminar l'admin
            for user in User.objects.exclude(is_superuser=True):
                user.delete()
                count += 1
            self.stdout.write(self.style.SUCCESS(f'✅ Eliminats {count} usuaris'))

        # Creem els grups i els usuaris dins d'una transacció atòmica
        with transaction.atomic():
            groups = self.create_groups()  # Creem grups si no existeixen
            users_created = self.create_users(options['users'], groups)  # Creem usuaris

        # Missatge final
        self.stdout.write(self.style.SUCCESS(f'✅ {users_created} usuaris creats correctament!'))

    # Funció que crea grups per roles si no existeixen
    def create_groups(self):
        group_names = ['Organitzadors', 'Participants', 'Moderadors']
        groups = {}
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)  # Obtenim o creem
            groups[name] = group
            if created:
                self.stdout.write(f'  ✓ Grup "{name}" creat')
        return groups  # Retornem diccionari de grups

    # Funció que crea els usuaris de prova
    def create_users(self, num_users, groups):
        users_created = 0

        # Creem un superusuari admin fix
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@streamevents.com',
                'first_name': 'Administrador',
                'last_name': '',
                'is_staff': True,
                'is_superuser': True,
                'display_name': '🔧 Administrador'
            }
        )
        if created:
            admin.set_password('admin123')  # Password inicial
            admin.save()
            self.stdout.write('  ✓ Superusuari admin creat')
            users_created += 1

        # Obtenim tots els usernames existents per evitar duplicats
        existing_usernames = set(User.objects.values_list('username', flat=True))

        # Creació d'usuaris de prova
        for i in range(1, num_users + 1):
            first_name = faker.first_name()  # Nom aleatori
            last_name = faker.last_name()    # Cognom aleatori
            base_username = f"{first_name}.{last_name}".lower()
            username = unidecode.unidecode(base_username)  # Eliminar accents
            username = ''.join(c for c in username if c.isalnum() or c == '.')  # Nom d'usuari net

            # Garantir unicitat del username
            suffix = 1
            unique_username = username
            while unique_username in existing_usernames:
                unique_username = f"{username}{suffix}"
                suffix += 1
            existing_usernames.add(unique_username)

            # Assignar rol i emoji segons el número d'usuari
            if i % 5 == 0:
                role = 'Organitzador'
                emoji = '🎯'
                group = groups['Organitzadors']
            elif i % 3 == 0:
                role = 'Moderador'
                emoji = '🛡️'
                group = groups['Moderadors']
            else:
                role = 'Participant'
                emoji = ''
                group = groups['Participants']

            # Nom complet amb emoji
            display_name = f"{emoji} {first_name} {last_name}".strip()
            # Biografia de prova
            bio = f"{role} d'esdeveniments en streaming, m'encanta la tecnologia i connectar amb la comunitat!"

            # Creem l'usuari
            user, created = User.objects.get_or_create(
                username=unique_username,
                defaults={
                    'email': f"{unique_username}@streamevents.com",
                    'first_name': first_name,
                    'last_name': last_name,
                    'display_name': display_name,
                    'bio': bio,
                    'is_active': True,
                }
            )

            if created:
                user.set_password('password123')  # Password inicial
                user.groups.add(group)  # Assignem el grup
                user.save()
                users_created += 1
                self.stdout.write(f'  ✓ Usuari {unique_username} ({role}) creat')

        return users_created  # Retornem el nombre d'usuaris creats