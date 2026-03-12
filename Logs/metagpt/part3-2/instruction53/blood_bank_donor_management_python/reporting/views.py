from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Report
from .utils import get_report_data
from django.utils import timezone

def is_admin_or_staff(user):
    return user.is_authenticated and (hasattr(user, 'role') and user.role in ['admin', 'superadmin', 'staff'])

@login_required
@user_passes_test(is_admin_or_staff)
def generate_report(request):
    """
    Generate a report based on user input.
    """
    if request.method == 'POST':
        report_type = request.POST.get('type')
        params = {}
        # Collect additional parameters as needed
        for key in request.POST:
            if key not in ['type', 'csrfmiddlewaretoken']:
                params[key] = request.POST[key]
        report = Report(type=report_type, created_at=timezone.now())
        # Generate report data using utility function
        report.data = get_report_data(report_type, params)
        report.params = params
        report.save()
        messages.success(request, f"{report.get_type_display()} report generated.")
        return redirect('report_detail', report_id=report.id)
    return render(request, 'generate_report.html')

@login_required
@user_passes_test(is_admin_or_staff)
def report_detail(request, report_id):
    """
    Show details of a generated report.
    """
    report = get_object_or_404(Report, pk=report_id)
    return render(request, 'report.html', {'report': report})

@login_required
@user_passes_test(is_admin_or_staff)
def export_report(request, report_id, format):
    """
    Export the report in the specified format (csv or json).
    """
    report = get_object_or_404(Report, pk=report_id)
    try:
        file_obj = report.export(format)
    except ValueError:
        return HttpResponseBadRequest("Unsupported export format.")
    # Set appropriate content type and headers
    if format == 'csv':
        content_type = 'text/csv'
    elif format == 'json':
        content_type = 'application/json'
    else:
        content_type = 'application/octet-stream'
    response = FileResponse(file_obj, as_attachment=True, filename=file_obj.name, content_type=content_type)
    return response