from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden

from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm

def event_list_view(request):
    search_form = EventSearchForm(request.GET)
    
    events = Event.objects.all()

    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        category = search_form.cleaned_data.get('category')
        status = search_form.cleaned_data.get('status')

        if search_query:
            events = events.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
        
        if category:
            events = events.filter(category=category)
        
        if status:
            events = events.filter(status=status)

    featured_events_qs = Event.objects.filter(is_featured__in=[True]).order_by()
    
    featured_events = sorted(featured_events_qs, key=lambda x: x.created_at, reverse=True)[:6]
    
    events = events.order_by('-created_at')

    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'object_list': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'featured_events': featured_events,
        'search_form': search_form,
    }
    return render(request, 'events/event_list.html', context)

def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_creator = request.user == event.creator
    context = {
        'event': event,
        'is_creator': is_creator,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def event_create_view(request):
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.status = 'scheduled'
            event.save()
            messages.success(request, "Esdeveniment creat correctament!")
            return redirect('events:event_detail', pk=event.pk)
        else:
            messages.error(request, "Hi ha errors al formulari.")
    else:
        form = EventCreationForm(user=request.user)
    
    return render(request, 'events/event_form.html', {'form': form, 'title': 'Crear Esdeveniment'})

@login_required
def event_update_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.user != event.creator:
        messages.error(request, "No tens permís per editar aquest esdeveniment.")
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        form = EventUpdateForm(request.POST, request.FILES, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Esdeveniment actualitzat correctament!")
            return redirect('events:event_detail', pk=pk)
        else:
            messages.error(request, "Hi ha errors al formulari.")
    else:
        form = EventUpdateForm(instance=event, user=request.user)

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Editar Esdeveniment'})

@login_required
def event_delete_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.user != event.creator:
        messages.error(request, "No tens permís per eliminar aquest esdeveniment.")
        return redirect('events:event_detail', pk=pk)

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Esdeveniment eliminat correctament!")
        return redirect('events:event_list')
    
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required
def my_events_view(request):
    status_filter = request.GET.get('status')
    events = Event.objects.filter(creator=request.user).order_by('-created_at')
    
    if status_filter:
        events = events.filter(status=status_filter)
        
    context = {
        'events': events,
        'object_list': events,
        'current_status': status_filter,
    }
    return render(request, 'events/my_events.html', context)

def events_by_category_view(request, category):
    valid_categories = [c[0] for c in Event.CATEGORY_CHOICES]
    if category not in valid_categories:
        messages.error(request, "Categoria no vàlida.")
        return redirect('events:event_list')

    events = Event.objects.filter(category=category).order_by('-created_at')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form_initial = EventSearchForm(initial={'category': category})

    context = {
        'page_obj': page_obj,
        'object_list': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'category': category,
        'search_form': form_initial
    }
    return render(request, 'events/event_list.html', context)