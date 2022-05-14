from django.shortcuts import render, HttpResponse, redirect
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
import sqlite3

from .forms import LoginForm
from .models import *
from datetime import datetime
# from .cv_drawer import *


def select_per(request):
    if request.user.is_authenticated:
        shops = Shop.objects.all()
        sessions = []
        for sh in Shift.objects.filter(shop_id=request.GET.get('shop')):
            start = datetime.fromtimestamp(int(sh.filmingTime[0]['start']))
            end = datetime.fromtimestamp(int(sh.filmingTime[-1]['end']))
            sessions.append([start.strftime("%m.%d.%Y, %H:%M") + ' - ' + end.strftime("%H:%M"), sh.id])
        if request.GET:
            get = request.GET
            shift = get.get('shift')
            date = get.get('date')
            time_start = get.get('time_start')
            time_stop = get.get('time_stop')
            if True or shift and date and time_stop and time_start:
                try:
                    time_start = datetime.strptime(date + ' ' + time_start, "%Y-%m-%d %H:%M").timestamp()
                    time_stop = datetime.strptime(date + ' ' + time_stop, "%Y-%m-%d %H:%M").timestamp()
                    print('/' + shift + '/' + str(int(time_start)) + '/' + str(int(time_stop)) + '/')
                    return redirect('per' + '/' + shift + '/' + str(int(time_start)) + '/' + str(int(time_stop)) + '/')
                except:
                    pass

        context = {
            'shops': shops,
            'sessions': sessions
        }
        return render(request, 'period_viewer/select.html', context)
    return redirect(reverse_lazy('login'))

def period(request, from_time, to_time, id_cofe):
    if request.user.is_authenticated:
        error = ''
        shift = Shift.objects.get(id=id_cofe)
        pers = shift.filmingTime
        try:
            all_time = Telemetry.objects.filter(time__lte=to_time).order_by('time').last().time - \
                       Telemetry.objects.filter(time__gte=from_time).order_by('time').first().time
            prev_telem = Telemetry.objects.filter(time__gte=from_time).order_by('time').first().time
        except:
            all_time = 0
            prev_telem = 0


        absent = False
        work_time, sum_absent, sum_work = [], 0, 0
        start_w = prev_telem
        for telem in Telemetry.objects.filter(time__gte=from_time, time__lte=to_time).order_by('time'):
            if telem.time - prev_telem > 60:
                prev = datetime.fromtimestamp(prev_telem)
                now = datetime.fromtimestamp(telem.time)
                stop_w = prev_telem
                delta = telem.time - prev_telem
                delta_w = stop_w - start_w
                work_time.append([datetime.fromtimestamp(start_w).strftime("%m.%d.%Y, %H:%M:%S"),
                                  datetime.fromtimestamp(stop_w).strftime("%H:%M:%S"),
                                  int(delta_w / 60), delta_w % 60, True])
                work_time.append([prev.strftime("%m.%d.%Y, %H:%M:%S"), now.strftime("%H:%M:%S"),
                                    int(delta/60), delta % 60, False])
                start_w = telem.time
                sum_absent += delta
                sum_work += delta_w
            prev_telem = telem.time
        video = None
        if prev_telem:
            if telem.time - start_w > 60:
                work_time.append([datetime.fromtimestamp(start_w).strftime("%m.%d.%Y, %H:%M:%S"),
                                  datetime.fromtimestamp(telem.time).strftime("%H:%M:%S"),
                                  int(delta_w / 60), delta_w % 60, True])
            video = '/media/' + shift.videos[0]['video']

        context = {
            'periods': pers,
            'all_time_h': all_time // 3600,
            'all_time_m': all_time % 3600 // 60,
            'all_time_s': all_time % 60,
            'work_time': work_time,
            'sum_absent': sum_absent,
            'sum_absent_sec': sum_absent % 60,
            'sum_absent_min': sum_absent // 60,
            'video': video
        }
        return render(request, 'period_viewer/period.html', context)
    return redirect(reverse_lazy('login'))


def logout_view(request):
    logout(request)
    return redirect(reverse_lazy('login'))


def user_login(request):
    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    error =  'Disabled account'
            else:
                error = 'Invalid login'
    else:
        form = LoginForm()
    return render(request, 'period_viewer/login.html', {'form': form, 'error': error})


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# def videoplayer(request):
#     context = {
#         'video': '/media/' + Telemetry.objects.first().shop.videos[0]['video']
#     }
#     return render(request, 'period_viewer/video.html', context)


def loader_db(request):
    if request.POST:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        if filename[-7:] == '.sqlite':
            try:
                new_db = sqlite3.connect('media/' + filename)
                db = sqlite3.connect('db-controller.sqlite')
                new_cursor = new_db.cursor()
                db_cursor = db.cursor()

                sqlite_select_query = "select * from shift"
                new_cursor.execute(sqlite_select_query)
                record = new_cursor.fetchall()
                for rec in record:
                    db_cursor.execute('insert OR IGNORE into shift values (?,?,?,?,?,?,?)', rec)

                sqlite_select_query = "select * from telemetry"
                new_cursor.execute(sqlite_select_query)
                record = new_cursor.fetchall()
                for rec in record:
                    db_cursor.execute('insert OR IGNORE into telemetry values (?,?,?,?,?,?,?,?,?,?)', rec)
                db.commit()

                db_cursor.close()
                new_cursor.close()

            except sqlite3.Error as error:
                print("Ошибка при подключении к sqlite", error)
            finally:
                if (new_db):
                    new_db.close()
                if (db):
                    db.close()
    return render(request, 'period_viewer/load.html')

