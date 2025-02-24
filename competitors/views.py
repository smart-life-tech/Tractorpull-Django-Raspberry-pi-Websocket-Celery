from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from competitors.tasks import send_ready_task, send_msg_to_screen_task

from .models import Class, Event, Competitor, Result

from datetime import date, datetime
import time

import glob
import serial

import csv
from django.http import HttpResponse

# below library is for the export option in competitors/result
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
# ----------------end -------------------------------------


# uri: 'competitors/
# action: redirect to 'competitors/run'
def index(request):
  return redirect('competitors:run')

# Export to csv and pdf commented out to allow for the 
# initial download options to work
# REMEMBER TO UNCOMMENT PATH IN URLS.PY
# def export_results(request):
#     event_id = request.GET.get('event_id')
#     export_format = request.GET.get('format', 'csv')
    
#     if event_id:
#         event = Event.objects.get(id=event_id)
#         results = Result.objects.filter(event_name=event.event_name)
#     else:
#         return HttpResponse("No event selected", status=400)
    
#     if export_format == 'pdf':
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="results_{event.event_name}.pdf"'
        
#         buffer = io.BytesIO()
#         doc = SimpleDocTemplate(buffer, pagesize=letter, title=f"Competition Results - {event.event_name}")
#         elements = []
#         styles = getSampleStyleSheet()
        
#         title = Paragraph(f"<b>Competition Results - {event.event_name}</b>", styles['Title'])
#         elements.append(title)
#         elements.append(Spacer(1, 12))
        
#         data = [['#', 'Competitor No', 'Name', 'Weight', 'Distance', 'Date', 'Time', 'Pull Factor']]
        
#         for idx, result in enumerate(results, start=1):
#             data.append([
#                 str(idx),
#                 str(result.competitor.competitor_no),
#                 result.competitor.competitor_name,
#                 str(result.weight),
#                 str(result.distance),
#                 str(result.run_date),
#                 str(result.run_time),
#                 str(result.pull_factor)
#             ])
        
#         table = Table(data, repeatRows=1)
#         table.setStyle(TableStyle([
#             ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#             ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#             ('GRID', (0, 0), (-1, -1), 1, colors.black)
#         ]))
        
#         elements.append(table)
#         doc.build(elements)
#         buffer.seek(0)
#         response.write(buffer.read())
#         return response
    
#     # Default to CSV export
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="results_{event.event_name}.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['#', 'Competitor No', 'Name', 'Weight', 'Distance', 'Date', 'Time', 'Pull Factor'])
    
#     for idx, result in enumerate(results, start=1):
#         writer.writerow([
#             idx,
#             result.competitor.competitor_no,
#             result.competitor.competitor_name,
#             result.weight,
#             result.distance,
#             result.run_date,
#             result.run_time,
#             result.pull_factor
#         ])
    
#     return response


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
  try:
    current_event = Event.objects.get(status=True)
  except Event.DoesNotExist:
    # Use the first event on the list as the default if the current event is not available
    current_event = Event.objects.first()
  results = Result.objects.filter(event_name=current_event.event_name).all()
  #results = Result.objects.filter(event_name=Event.objects.get(status=True).event_name).all()
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
    event_name = request.GET.get("event_name")  # Get event name from URL query params          
    results = Result.objects.all()
    
    if event_name:
        results = results.filter(competitor__result__event_name=event_name).distinct()  
    
    events = Event.objects.all().values("id", "event_name").distinct()
    current_event = Event.objects.filter(status=True).first()    

    return render(request, "components/results.html", {
        "results": results,
        "current_event": current_event,
        "events": events,
        "selected_event": event_name  # Pass selected event back to the template
    })


# uri: 'competitors/setup'
# action: edit class and event
def setup(request):
  classes = Class.objects.all()
  events = Event.objects.all()
  #current_event = Event.objects.get(status=True)
  try:
    current_event = Event.objects.get(status=True)
  except Event.DoesNotExist:
    # Use the first event on the list as the default if the current event is not available
    current_event = Event.objects.first()

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
    
    # Fetch class object
    try:
        selected_class = Class.objects.get(class_name=request.POST.get('clasS'))
    except Class.DoesNotExist:
        return HttpResponse("Error: Selected class does not exist.", status=400)

    # Ensure pull_factor is set
    pull_factor = request.POST.get('pull_factor')
    if not pull_factor:  # If not provided, fetch from the class
        pull_factor = selected_class.pull_factor

    competitor, created = Competitor.objects.get_or_create(
        competitor_no=no,
        event=current_event,
        defaults={
            'competitor_name': request.POST.get('competitor_name'),
            'tractor_name': request.POST.get('tractor_name'),
            'weight': request.POST.get('competitor_weight'),
            'clasS': Class.objects.get(class_name=request.POST.get('clasS')),
            'pull_factor': pull_factor
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
  #t = time.localtime()
  #  current_time = time.strftime("%H:%M:%S", t)
  t = datetime.now()
  current_time = t.strftime("%H:%M:%S")

  
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


