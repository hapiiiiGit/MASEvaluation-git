from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse
from .models import AdminUser, AuditLog
from .forms import AdminUserForm
from django.utils import timezone

def is_admin(user):
    return user.is_authenticated and user.role in ['admin', 'superadmin']

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """
    Admin dashboard view: shows overview statistics and recent activity.
    """
    user_count = AdminUser.objects.count()
    active_users = AdminUser.objects.filter(is_active=True).count()
    recent_logs = AuditLog.objects.order_by('-timestamp')[:10]
    context = {
        'user_count': user_count,
        'active_users': active_users,
        'recent_logs': recent_logs,
    }
    return render(request, 'admin_panel.html', context)

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """
    View and manage admin users.
    """
    users = AdminUser.objects.all()
    if request.method == 'POST':
        if 'add_user' in request.POST:
            form = AdminUserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                AuditLog.objects.create(
                    user=request.user,
                    action='create',
                    description=f"Created admin user {user.username}",
                    timestamp=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f"Admin user {user.username} created.")
                return redirect('manage_users')
            else:
                messages.error(request, "Please correct the errors below.")
        elif 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user_to_delete = get_object_or_404(AdminUser, pk=user_id)
            if user_to_delete != request.user:
                username = user_to_delete.username
                user_to_delete.delete()
                AuditLog.objects.create(
                    user=request.user,
                    action='delete',
                    description=f"Deleted admin user {username}",
                    timestamp=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, f"Admin user {username} deleted.")
            else:
                messages.error(request, "You cannot delete your own account.")
            return redirect('manage_users')
    else:
        form = AdminUserForm()
    context = {
        'users': users,
        'form': form,
    }
    return render(request, 'manage_users.html', context)

@login_required
@user_passes_test(is_admin)
def audit_logs(request):
    """
    View audit logs for admin actions.
    """
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    context = {
        'logs': logs,
    }
    return render(request, 'audit_logs.html', context)