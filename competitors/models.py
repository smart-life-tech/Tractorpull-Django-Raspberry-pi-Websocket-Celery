from django.db import models


class Event(models.Model):
    event_name = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=False)


class Class(models.Model):
    class_name = models.CharField(max_length=50, unique=True)
    pull_factor = models.IntegerField(default=85)


class Competitor(models.Model):
    competitor_no = models.IntegerField()
    competitor_name = models.CharField(max_length=50)
    tractor_name = models.CharField(max_length=50, null=True)
    weight = models.IntegerField()
    clasS = models.ForeignKey(Class, on_delete=models.CASCADE)
    pull_factor = models.IntegerField(default=85)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)


class Result(models.Model):
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    weight = models.IntegerField(default=0)
    pull_factor = models.IntegerField(default=85)
    distance = models.FloatField()
    run_date = models.DateField('date run')
    run_time = models.TimeField('time run')
    event_name = models.CharField(max_length=50)



