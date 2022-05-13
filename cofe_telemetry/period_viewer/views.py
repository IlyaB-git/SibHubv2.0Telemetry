from django.shortcuts import render, HttpResponse
from .models import *
from datetime import datetime
# from .cv_drawer import *


def select_per(request):
    sessions = []
    for sh in Shift.objects.all():
        start = datetime.fromtimestamp(int(sh.filmingTime[0]['start']))
        end = datetime.fromtimestamp(int(sh.filmingTime[-1]['end']))
        sessions.append([start.strftime("%m/%d/%Y, %H:%M:%S"), end.strftime("%m/%d/%Y, %H:%M:%S")])
    context = {
        'sessions': sessions
    }
    return render(request, 'period_viewer/select.html', context)

def period(request, from_time, to_time, id_cofe):
    pers, time_work = [], 0
    shift = Shift.objects.get(id=id_cofe)
    pers += shift.filmingTime
    try:
        all_time = Telemetry.objects.filter(time__gte=from_time)[-1] - \
                   Telemetry.objects.filter(time__lte=to_time)[0]
        prev_telem = Telemetry.objects.first().time
    except:
        all_time = 0
    absent = False
    absent_time, sum_absent = [], 0
    for telem in Telemetry.objects.filter(time__gte=from_time, time__lte=to_time):
        if telem.time - prev_telem > 60:
            prev = datetime.fromtimestamp(prev_telem)
            now = datetime.fromtimestamp(telem.time)
            delta = telem.time - prev_telem
            absent_time.append([prev.strftime("%m/%d/%Y, %H:%M:%S"), now.strftime("%m/%d/%Y, %H:%M:%S"),
                                int(delta/60), delta % 60])
            sum_absent += delta
        prev_telem = telem.time

    context = {
        'periods': pers,
        'time_work': time_work,
        'all_time_h': all_time // 3600,
        'all_time_m': all_time % 3600 // 60,
        'all_time_s': all_time % 60,
        'absent_time': absent_time,
        'sum_absent': sum_absent,
        'sum_absent_sec': sum_absent % 60,
        'sum_absent_min': sum_absent // 60
    }
    return render(request, 'period_viewer/period.html', context)

def login(request):
    return render(request, 'period_viewer/login.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def videoplayer(request):
    context = {
        'video': '/media/' + Shift.objects.first().videos[0]['video']
    }
    return render(request, 'period_viewer/video.html', context)



