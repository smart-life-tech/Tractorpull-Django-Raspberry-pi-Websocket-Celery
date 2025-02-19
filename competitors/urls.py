from django.urls import path

from . import views

from .model import _class, event

app_name = 'competitors'
urlpatterns = [
    path('', views.index, name='index'),
    path('run/', views.run, name='run'),
    path('results/', views.results, name='results'),
    path('setup/', views.setup, name='setup'),

    path('run/send_ready/', views.send_ready, name='send_ready'),
    path('run/competitor/', views.save_competitor, name='save_competitor'),
    path('run/save_result/', views.save_result, name='save_result'),
    path('run/reset/', views.reset, name='reset'),
    path('run/send_msg_to_screen/', views.send_msg_to_screen, name='send_msg_to_screen'),

    path('classes/', _class.index, name='classes'),
    path('classes/delete/<int:id>/', _class.delete, name="delete_class"),
    path('classes/update/<name>/', _class.update, name="update_class"),

    path('events/', event.index, name='events'),
    path('events/delete/<int:id>/', event.delete, name="delete_event"),
    path('events/<int:id>/', event.set_current_event, name="set_current_event"),
    # path('results/export/', views.export_results, name='export_results'),
]