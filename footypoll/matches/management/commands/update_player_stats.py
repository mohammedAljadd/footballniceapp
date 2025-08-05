from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from matches.models import PlayerStats

class Command(BaseCommand):
    help = 'Update player statistics for all users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Update stats for a specific username only',
        )

    def handle(self, *args, **options):
        username = options.get('user')
        users_updated = 0
        
        if username:
            try:
                user = User.objects.get(username=username)
                PlayerStats.update_stats_for_user(user)
                users_updated = 1
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated statistics for user: {username}')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" does not exist')
                )
                return
        else:
            # Update all users
            for user in User.objects.all():
                PlayerStats.update_stats_for_user(user)
                users_updated += 1
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated statistics for {users_updated} users')
            )