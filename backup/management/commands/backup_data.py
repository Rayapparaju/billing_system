import json
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from io import StringIO

class Command(BaseCommand):
    help = 'Backup all data as JSON files'

    def handle(self, *args, **options):
        backup_dir = settings.BACKUP_DIR
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        apps = ['customers', 'suppliers', 'products', 'accounts', 'sales', 'purchases']
        summary = {}
        for app in apps:
            filename = f'{app}_{timestamp}.json'
            filepath = os.path.join(backup_dir, filename)
            out = StringIO()
            try:
                call_command('dumpdata', app, '--indent', '2', stdout=out)
                data = out.getvalue()
                with open(filepath, 'w') as f:
                    f.write(data)
                count = len(json.loads(data))
                summary[app] = {'file': filename, 'records': count}
                self.stdout.write(self.style.SUCCESS(f'{app}: {count} records -> {filename}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'{app}: Failed - {e}'))
        manifest = {
            'timestamp': timestamp,
            'backup_dir': str(backup_dir),
            'summary': summary,
        }
        manifest_path = os.path.join(backup_dir, f'manifest_{timestamp}.json')
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        self.stdout.write(self.style.SUCCESS(f'Manifest: {manifest_path}'))
