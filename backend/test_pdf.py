import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import DatasetHistory
from api.utils import generate_pdf_report

try:
    ds = DatasetHistory.objects.get(id=17)
    print(f'Dataset: {ds.filename}')
    print('Generating PDF...')
    pdf = generate_pdf_report(ds)
    print(f'✓ PDF generated successfully! Size: {len(pdf.getvalue())} bytes')
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
