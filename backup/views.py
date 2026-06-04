import os
import json
import zipfile
from io import BytesIO
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.core.management import call_command
from io import StringIO

@login_required
def backup_list(request):
    backup_dir = settings.BACKUP_DIR
    backups = []
    if os.path.exists(backup_dir):
        for f in sorted(os.listdir(backup_dir), reverse=True):
            if f.endswith('.json') and not f.startswith('manifest'):
                parts = f.split('_')
                if len(parts) >= 2:
                    app = parts[0]
                    ts = parts[1].replace('.json', '')
                    try:
                        dt = datetime.strptime(ts, '%Y%m%d_%H%M%S')
                        size = os.path.getsize(os.path.join(backup_dir, f))
                        backups.append({'app': app, 'file': f, 'date': dt, 'size': f'{size/1024:.1f} KB'})
                    except:
                        pass
    return render(request, 'backup/list.html', {'backups': backups})

@login_required
def backup_create(request):
    if request.method == 'POST':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        apps = ['customers', 'suppliers', 'products', 'accounts', 'sales', 'purchases']
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for app in apps:
                out = StringIO()
                try:
                    call_command('dumpdata', app, '--indent', '2', stdout=out)
                    zf.writestr(f'{app}_{timestamp}.json', out.getvalue())
                except Exception as e:
                    zf.writestr(f'{app}_{timestamp}.json', json.dumps({'error': str(e)}))
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="backup_{timestamp}.zip"'
        return response
    return render(request, 'backup/create.html')
