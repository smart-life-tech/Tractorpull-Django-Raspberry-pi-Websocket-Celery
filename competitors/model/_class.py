from competitors.models import Class
from django.shortcuts import redirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        pull_factor = request.POST.get('pull_factor')
        new_class = Class(class_name=class_name, pull_factor=pull_factor)
        new_class.save()
        return redirect('competitors:setup')

def delete(request, id):
    deleting_class = Class.objects.get(id=id)
    deleting_class.delete()
    return redirect('competitors:setup')

@csrf_exempt
def update(request, name):
    pull_factor = request.POST.get('pull_factor')
    c = Class.objects.get(class_name=name)
    c.pull_factor = int(pull_factor)
    c.save()
    return HttpResponse('success')