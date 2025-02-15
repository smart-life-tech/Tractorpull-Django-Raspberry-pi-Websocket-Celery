from django.contrib import admin

from .models import Event, Class, Competitor, Result


class ClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'class_name', 'pull_factor')


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'event_name', 'status')


class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'competitor_no', 'competitor_name', 'tractor_name', 'weight', 'clasS', 'pull_factor', 'event')


admin.site.register(Event, EventAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Competitor, CompetitorAdmin)
admin.site.register(Result)
