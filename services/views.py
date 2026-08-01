from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required
from workers.models import WorkerProfile

from .models import FavoriteService, Service
from .forms import ServiceForm


def _get_related_workers(service):
    category_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__is_verified_worker=True,
        service_category__icontains=service.category,
    )
    skill_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__is_verified_worker=True,
        skills__icontains=service.category,
    )
    direct_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__is_verified_worker=True,
        service=service,
    )

    combined = (category_matches | skill_matches | direct_matches).distinct().select_related('user')[:4]
    return combined


def service_list(request):
    search_query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    location = request.GET.get('location', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_rating = request.GET.get('min_rating', '')
    sort = request.GET.get('sort', '')

    services = Service.objects.filter(is_available=True).annotate(
        avg_rating=Avg('bookings__reviews__rating'),
        booking_count=Count('bookings')
    )

    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if category:
        services = services.filter(category=category)

    if location:
        services = services.filter(location__icontains=location)

    if min_price:
        services = services.filter(price__gte=min_price)

    if max_price:
        services = services.filter(price__lte=max_price)

    if min_rating:
        services = services.filter(avg_rating__gte=min_rating)

    if sort == 'price_asc':
        services = services.order_by('price')
    elif sort == 'price_desc':
        services = services.order_by('-price')
    elif sort == 'rating_desc':
        services = services.order_by('-avg_rating')
    elif sort == 'popular':
        services = services.order_by('-booking_count')
    else:
        services = services.order_by('-featured', '-avg_rating', 'name')

    categories = [choice[0] for choice in Service.SERVICE_CHOICES]
    locations = Service.objects.filter(location__isnull=False).values_list('location', flat=True).distinct()
    rating_options = [5, 4, 3, 2, 1]

    services = list(services)
    for service in services:
        service.related_workers = _get_related_workers(service)

    featured_services = [service for service in services if service.featured][:4]
    popular_services = sorted(services, key=lambda service: service.booking_count, reverse=True)[:4]

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
            'min_price': min_price,
            'max_price': max_price,
            'min_rating': min_rating,
            'sort': sort,
        }
    )


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    verified_workers = _get_related_workers(service)
    service.related_workers = verified_workers

    is_favorited = False
    if request.user.is_authenticated and request.user.role == 'customer':
        is_favorited = FavoriteService.objects.filter(
            customer=request.user,
            service=service
        ).exists()

    return render(
        request,
        'services/service_detail.html',
        {
            'service': service,
            'verified_workers': verified_workers,
            'is_favorited': is_favorited,
        }
    )


@login_required
def toggle_favorite_service(request, pk):
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can favorite services.')
        return redirect('service_detail', pk=pk)

    service = get_object_or_404(Service, pk=pk)
    favorite, created = FavoriteService.objects.get_or_create(
        customer=request.user,
        service=service
    )
    if not created:
        favorite.delete()
        messages.success(request, 'Service removed from favorites.')
    else:
        messages.success(request, 'Service added to favorites.')

    return redirect('service_detail', pk=pk)


@admin_required
def create_service(request):

    if request.method == 'POST':

        form = ServiceForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            form.save()
            return redirect('service_list')

    else:
        form = ServiceForm()

    return render(
        request,
        'services/create_service.html',
        {'form': form}
    )


@admin_required
def edit_service(request, pk):

    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':

        form = ServiceForm(
            request.POST,
            request.FILES,
            instance=service
        )

        if form.is_valid():
            form.save()
            return redirect('service_detail', pk=pk)

    else:
        form = ServiceForm(instance=service)

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
    service = get_object_or_404(Service, pk=pk)

    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully.')
        return redirect('service_list')

    return render(
        request,
        'services/delete_service.html',
        {'service': service}
    )