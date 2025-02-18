from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from competitors.tasks import send_ready_task, send_msg_to_screen_task

from .models import Class, Event, Competitor, Result

from datetime import date
import time

import glob
import serial

import csv
from django.http import HttpResponse

# uri: 'competitors/
# action: redirect to 'competitors/run'
def index(request):
  return redirect('competitors:run')

def export_results(request):
    current_event = Event.objects.get(status=True)
    results = Result.objects.filter(event_name=current_event.event_name)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="results.csv"'

    writer = csv.writer(response)
    writer.writerow(['Competitor No', 'Name', 'Weight', 'Distance', 'Date', 'Time', 'Pull Factor'])
    
    for result in results:
        writer.writerow([result.competitor.competitor_no, result.competitor.competitor_name, result.weight, result.distance, result.run_date, result.run_time, result.pull_factor])

    return response


# uri: 'competitors/run'
# action: show run page with data of class, competitor, result
def run(request):
  port = '/dev/ttyUSB0'

  result = None
  try:
    s = serial.Serial(port)
    s.close()
    result = port
  except (OSError, serial.SerialException):
    pass

  connection = 'Disconnected'
  if result:
    connection = 'Connected'

  classes = Class.objects.all()
  results = Result.objects.filter(event_name=Event.objects.get(status=True).event_name).all()
  current_event = Event.objects.get(status=True)
  competitors = Competitor.objects.filter(event=current_event).all()

  for competitor in competitors:
    competitor.clasS.id -= Class.objects.first().id

  return render(request, 'components/run.html', {
    'classes': classes,
    'current_event': current_event,
    'results': results,
    'competitors': competitors,
    'connection': connection
  })

# uri: 'competitors/results'
# action: show the competition results
def results(request):
  results = Result.objects.all()
  current_event = Event.objects.get(status=True)

  return render(request, 'components/results.html', {
    'results': results,
    'current_event': current_event
  })

# uri: 'competitors/setup'
# action: edit class and event
def setup(request):
  classes = Class.objects.all()
  events = Event.objects.all()
  current_event = Event.objects.get(status=True)

  return render(request, 'components/setup.html', {
    'classes': classes,
    'events': events,
    'current_event': current_event
  })

# uri: 'competitors/send_ready'
# action: send ready msg to rs232
@csrf_exempt
def send_ready(request):
  pull_factor = request.POST.get('pull_factor')
  weight = request.POST.get('weight')
  global current_task
  current_task = send_ready_task.delay(pull_factor, weight)
  return HttpResponse('success')

@csrf_exempt
def reset(request):
  global current_task
  current_task.revoke(terminate=True)
  return HttpResponse('success')

@csrf_exempt
def send_msg_to_screen(request):
  send_msg_to_screen_task.delay(request.POST.get('msg'))
  return HttpResponse('success')

# @csrf_exempt
# def save_competitor(request):
#   no = request.POST.get('competitor_no')
#   if Competitor.objects.filter(competitor_no=no, event=Event.objects.get(status=True)):
#     competitor = Competitor.objects.get(competitor_no=no, event=Event.objects.get(status=True))
#   else:
#     competitor = Competitor()
#   competitor.competitor_no = request.POST.get('competitor_no')
#   competitor.competitor_name = request.POST.get('competitor_name')
#   competitor.tractor_name = request.POST.get('tractor_name')
#   competitor.weight = request.POST.get('competitor_weight')
#   competitor.clasS = Class.objects.get(class_name=request.POST.get('clasS'))
#   competitor.pull_factor = request.POST.get('pull_factor')
#   competitor.event = Event.objects.get(status=True)
#   competitor.save()

#   c = Class.objects.get(class_name=request.POST.get('clasS'))
#   if not c.pull_factor == competitor.pull_factor:
#     c.pull_factor = competitor.pull_factor
#     c.save()

#   return HttpResponse('success!')

@csrf_exempt
def save_competitor(request):
    no = request.POST.get('competitor_no')
    current_event = Event.objects.get(status=True)
    
    competitor, created = Competitor.objects.get_or_create(
        competitor_no=no,
        event=current_event,
        defaults={
            'competitor_name': request.POST.get('competitor_name'),
            'tractor_name': request.POST.get('tractor_name'),
            'weight': request.POST.get('competitor_weight'),
            'clasS': Class.objects.get(class_name=request.POST.get('clasS')),
            'pull_factor': request.POST.get('pull_factor')
        }
    )
    
    if not created:
        # Update only if the class is changed
        if competitor.clasS.class_name != request.POST.get('clasS'):
            competitor.clasS = Class.objects.get(class_name=request.POST.get('clasS'))
        
        # Update pull factor only if it has changed
        if competitor.pull_factor != request.POST.get('pull_factor'):
            competitor.pull_factor = request.POST.get('pull_factor')
        
        competitor.save()

    return HttpResponse('success!')
  

@csrf_exempt
def save_result(request):
  competitor_no = request.POST.get('competitor_no')
  weight = request.POST.get('weight')
  pull_factor = request.POST.get('pull_factor')
  distance = request.POST.get('distance')
  competitor = Competitor.objects.get(competitor_no=competitor_no, event=Event.objects.get(status=True))
  t = time.localtime()
  current_time = time.strftime("%H:%M:%S", t)
  result = Result(
    competitor = competitor,
    weight = int(weight),
    pull_factor = int(pull_factor),
    distance = float(distance),
    run_date = date.today(),
    run_time = current_time,
    event_name = Event.objects.last().event_name
  )
  result.save()
  return HttpResponse('success')


