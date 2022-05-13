from django.db import models

class Shift(models.Model):
    id = models.TextField(primary_key=True)
    filmingTime = models.JextField()
    videos = models.JextField()
    motion = models.JextField()
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()

    class Meta:
        db_table = 'shift'
'''
class SqliteSequence(models.Model):
    name = models.TextField()
    seq = models.TextField()

    class Meta:
        db_table = 'sqlite_sequence'
        '''

class Telemetry(models.Model):
    id = models.TextField(primary_key=True)
    time = models.IntegerField()
    detectionProbability = models.FloatField()
    detectionCoordinates = models.JextField()
    commentary = models.JextField()
    isSent = models.IntegerField()
    videoName = models.TextField()
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    shiftId = models.TextField()

    class Meta:
        db_table = 'telemetry'


