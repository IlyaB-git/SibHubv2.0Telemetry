from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=64)
    address = models.TextField()

    class Meta:
        db_table = 'shop'
        verbose_name='Заведение'
        verbose_name_plural='Заведения'

class Shift(models.Model):
    id = models.TextField(primary_key=True)
    filmingTime = models.JSONField()
    videos = models.JSONField()
    motion = models.JSONField()
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'shift'
        verbose_name='Запись'
        verbose_name_plural='Записи'
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
    detectionCoordinates = models.JSONField()
    commentary = models.JSONField()
    isSent = models.IntegerField()
    videoName = models.TextField()
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    shiftId = models.TextField()

    class Meta:
        db_table = 'telemetry'
        verbose_name='Телеметрия'
        verbose_name_plural='Телеметрия'

