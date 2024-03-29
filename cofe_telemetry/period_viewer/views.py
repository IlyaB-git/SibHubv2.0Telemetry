from django.shortcuts import render, HttpResponse, redirect
from django.http import StreamingHttpResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
import sqlite3

from .forms import LoginForm
from .models import *
from datetime import datetime
from .services import open_file
from .detection import detect
# from .cv_drawer import *


def select_per(request):
    if request.user.is_authenticated:
        shops_i, _ = Premisions.objects.get_or_create(user_id=request.user.id)
        shops = []
        if shops_i.shops:
            for id in shops_i.shops:
                shops += Shop.objects.filter(id=id)
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
            try:
                check = str(Shift.objects.get(pk=shift).shop_id) == get.get('shop')
            except:
                check = False
            if shift and date and time_stop and time_start and check:
                try:
                    time_start = datetime.strptime(date + ' ' + time_start, "%Y-%m-%d %H:%M").timestamp()
                    time_stop = datetime.strptime(date + ' ' + time_stop, "%Y-%m-%d %H:%M").timestamp()
                    print('/' + shift + '/' + str(int(time_start)) + '/' + str(int(time_stop)) + '/')
                    return redirect('per' + '/' + shift + '/' + str(int(time_start)) + '/' + str(int(time_stop)) + '/')
                except:
                    pass

        context = {
            'shops': shops,
            'sessions': sessions,
            'full_form': bool(len(shops))
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
        work_time, sum_absent, sum_work, customersl = [], 0, 0, []
        start_w = prev_telem
        cust_in = prev_telem
        prev_cust = prev_telem
        for telem in Telemetry.objects.filter(time__gte=from_time, time__lte=to_time).order_by('time'):
            prev_telem, cust_in, start_w, sum_absent, sum_work, work_time, customersl =\
                detect(telem, prev_telem, cust_in, start_w, sum_absent, sum_work, work_time, customersl)



        video = None
        if prev_telem:
            detect(telem, prev_telem, cust_in, start_w, sum_absent, sum_work, work_time, customersl, True)
            if telem.time - prev_telem > 3:
                customersl.append([telem.time - prev_telem, False])
            if prev_telem - cust_in > 3:
                customersl.append([prev_telem - cust_in, True])

            video = '/video/' + shift.videos[0]['video']

        raspred = [[i[-2],str(round((int(i[-1]))/int(all_time)*100, 2))] for i in work_time]
        customers = [[str(round(c[0]*100/all_time, 2)), c[1]] for c in customersl]
        num_custs = 0
        for i in customers:
            if i[1] == 0:
                num_custs += 1

        context = {
            'periods': pers,
            'all_time':raspred,
            'all_time_h': all_time // 3600,
            'all_time_m': all_time % 3600 // 60,
            'all_time_s': all_time % 60,
            'work_time': work_time,
            'sum_absent': sum_absent,
            'sum_absent_sec': sum_absent % 60,
            'sum_absent_min': sum_absent // 60,
            'sum_work_h': sum_work // 3600,
            'sum_work_sec': sum_work % 60,
            'sum_work_min': sum_work // 60,
            'video': video,
            'customers': customers,
            'num_custs': num_custs
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
    error = ''
    if request.POST:
        try:
            myfile = request.FILES['myfile']
        except:
            return render(request, 'period_viewer/load.html', {'error': 'Ошибка загрузки'})
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
    return render(request, 'period_viewer/load.html', {'error': error})





def get_streaming_video(request, video_pk: str):
    file, status_code, content_length, content_range = open_file(request, video_pk)
    response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')

    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(content_length)
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = content_range
    return response