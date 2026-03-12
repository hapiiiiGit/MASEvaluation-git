from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Donor
from .forms import DonorForm
from .firebase import FirebaseService
from django.contrib import messages

firebase_service = FirebaseService()

def donor_list(request):
    """
    List all donors, optionally filter by blood type and location.
    Data is fetched from Firebase for real-time sync.
    """
    blood_type = request.GET.get('blood_type', '')
    location = request.GET.get('location', '')

    donors = firebase_service.get_donors()
    if blood_type:
        donors = [d for d in donors if d.blood_type == blood_type]
    if location:
        donors = [d for d in donors if d.location.lower() == location.lower()]

    context = {
        'donors': donors,
        'blood_type': blood_type,
        'location': location,
    }
    return render(request, 'donor_list.html', context)

def donor_detail(request, donor_id):
    """
    Show details for a single donor.
    """
    donor = firebase_service.get_donor(donor_id)
    if not donor:
        return HttpResponse("Donor not found.", status=404)
    return render(request, 'donor_detail.html', {'donor': donor})

def donor_create(request):
    """
    Create a new donor record.
    """
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            firebase_service.add_donor(donor)
            messages.success(request, "Donor registered successfully.")
            return redirect('donor_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DonorForm()
    return render(request, 'donor_form.html', {'form': form})

def donor_edit(request, donor_id):
    """
    Edit an existing donor record.
    """
    donor = firebase_service.get_donor(donor_id)
    if not donor:
        return HttpResponse("Donor not found.", status=404)
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            donor = form.save(commit=False)
            firebase_service.update_donor(donor)
            messages.success(request, "Donor information updated.")
            return redirect('donor_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DonorForm(instance=donor)
    return render(request, 'donor_form.html', {'form': form, 'edit': True, 'donor_id': donor_id})

def donor_delete(request, donor_id):
    """
    Delete a donor record.
    """
    donor = firebase_service.get_donor(donor_id)
    if not donor:
        return HttpResponse("Donor not found.", status=404)
    if request.method == 'POST':
        firebase_service.delete_donor(donor_id)
        messages.success(request, "Donor deleted successfully.")
        return redirect('donor_list')
    return render(request, 'donor_confirm_delete.html', {'donor': donor})