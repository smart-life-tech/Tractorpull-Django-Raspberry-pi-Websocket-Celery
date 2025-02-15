from competitors.models import Event

from django.shortcuts import render, redirect, reverse

def index(request):
    if request.method == 'POST':
        current_event = Event.objects.get(status=True)
        current_event.status = False
        current_event.save()
        event_name = request.POST.get('event_name')
        new_event = Event(event_name=event_name, status=True)
        new_event.save()
        return redirect('competitors:setup')

def delete(request, id):
    event = Event.objects.get(id=id)
    event.delete()
    return redirect('competitors:setup')

def set_current_event(request, id):
    old = Event.objects.get(status=True)
    if not old.id == id:
        old.status = False
        current = Event.objects.get(id=id)
        current.status = True
        old.save()
        current.save()
    return redirect('competitors:setup')