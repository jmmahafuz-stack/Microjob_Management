from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required
from workers.models import WorkerProfile

from .models import Service, Category
from .forms import ServiceForm


def ensure_sample_services():
    """Populate the service catalog with realistic examples when the database is empty."""

    if Service.objects.exists():
        return

    # Ensure categories exist
    plumbing_cat, _ = Category.objects.get_or_create(name='Plumbing')
    electrical_cat, _ = Category.objects.get_or_create(name='Electrical')
    cleaning_cat, _ = Category.objects.get_or_create(name='Cleaning')

    sample_services = [
        {
            'name': 'Plumbing Repair',
            'category': plumbing_cat,
            'description': 'Fast repair for leaks, pipe replacement, and faucet installation.',
            'price': '1200.00',
            'image': 'service_images/images_1.jpg',
            'duration': '2 hours',
            'location': 'Dhaka',
            'featured': True,
            'is_available': True,
        },
        {
            'name': 'Electrical Wiring',
            'category': electrical_cat,
            'description': 'Safe electrical diagnostics, rewiring, and installation work.',
            'price': '1500.00',
            'image': 'service_images/images_2.jpg',
            'duration': '3 hours',
            'location': 'Dhaka',
            'featured': True,
            'is_available': True,
        },
        {
            'name': 'Home Cleaning',
            'category': cleaning_cat,
            'description': 'Routine house cleaning and deep-clean services for busy households.',
            'price': '900.00',
            'image': 'service_images/images_3.jpg',
            'duration': '2 hours',
            'location': 'Chattogram',
            'featured': False,
            'is_available': True,
        },
    ]

    for payload in sample_services:
        Service.objects.get_or_create(
            name=payload['name'],
            defaults=payload,
        )


def _get_related_workers(service):
    """Get workers that match the service's category."""
    # Get workers approved in this service's category
    category_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__worker_status='APPROVED',
        categories=service.category,
    )

    # Also include workers with relevant skills
    skill_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__worker_status='APPROVED',
        skills__icontains=service.category.name,
    )

    # Combine and get unique workers
    combined = (
        category_matches |
        skill_matches
    ).distinct().select_related('user')[:4]

    return combined


def service_list(request):
    ensure_sample_services()

    search_query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    min_rating = request.GET.get('min_rating', '')
    sort = request.GET.get('sort', '')

    services = Service.objects.filter(
        is_available=True
    ).annotate(
        avg_rating=Avg('bookings__reviews__rating'),
        booking_count=Count('bookings')
    )

    # Search
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Category filter
    if category:
        services = services.filter(
            category__name=category
        )

    # Location filter
    if location:
        services = services.filter(
            location__icontains=location
        )

    # Rating filter
    if min_rating:
        services = services.filter(
            avg_rating__gte=min_rating
        )

    # Sorting
    if sort == 'rating_desc':
        services = services.order_by('-avg_rating')

    elif sort == 'popular':
        services = services.order_by('-booking_count')

    else:
        services = services.order_by(
            '-featured',
            '-avg_rating',
            'name'
        )

    # Get all active categories for the filter dropdown
    categories = list(Category.objects.filter(is_active=True).values_list('name', flat=True))

    locations = (
        Service.objects
        .filter(location__isnull=False)
        .values_list('location', flat=True)
        .distinct()
    )

    rating_options = [5, 4, 3, 2, 1]

    services = list(services)

    # Find available workers for every service
    for service in services:
        service.related_workers = _get_related_workers(service)

    featured_services = [
        service
        for service in services
        if service.featured
    ][:4]

    popular_services = sorted(
        services,
        key=lambda service: service.booking_count,
        reverse=True
    )[:4]

    return render(
        request,
        'services/service_list.html',
        {
            'services': services,
            'featured_services': featured_services,
            'popular_services': popular_services,

            'categories': categories,
            'locations': locations,
            'rating_options': rating_options,

            'search_query': search_query,
            'selected_category': category,
            'selected_location': location,

            'min_rating': min_rating,
            'sort': sort,
        }
    )


def service_detail(request, pk):
    service = get_object_or_404(
        Service,
        pk=pk
    )

    verified_workers = _get_related_workers(
        service
    )

    service.related_workers = verified_workers

    return render(
        request,
        'services/service_detail.html',
        {
            'service': service,
            'verified_workers': verified_workers,
        }
    )


@admin_required
def create_service(request):

    if request.method == 'POST':

        form = ServiceForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()

            return redirect(
                'service_list'
            )

    else:
        form = ServiceForm()

    return render(
        request,
        'services/create_service.html',
        {
            'form': form
        }
    )


@admin_required
def edit_service(request, pk):

    service = get_object_or_404(
        Service,
        pk=pk
    )

    if request.method == 'POST':

        form = ServiceForm(
            request.POST,
            request.FILES,
            instance=service
        )

        if form.is_valid():
            form.save()

            return redirect(
                'service_detail',
                pk=pk
            )

    else:
        form = ServiceForm(
            instance=service
        )

    return render(
        request,
        'services/edit_service.html',
        {
            'form': form,
            'service': service
        }
    )


@admin_required
def delete_service(request, pk):

    service = get_object_or_404(
        Service,
        pk=pk
    )

    if request.method == 'POST':

        service.delete()

        messages.success(
            request,
            'Service deleted successfully.'
        )

        return redirect(
            'service_list'
        )

    return render(
        request,
        'services/delete_service.html',
        {
            'service': service
        }
    )