from datetime import datetime

def detect(telem, prev_telem, cust_in, start_w, sum_absent, sum_work, work_time, customersl, end=False):
    x = (telem.detectionCoordinates['x1'] + telem.detectionCoordinates['x2']) / 2
    y = (telem.detectionCoordinates['y1'] + telem.detectionCoordinates['y2']) / 2
    if ((1120 - x) * (- 1080) - (800) * (1080 - y) > 0) or ((x - 800) * 1080 + 800 * (1080 - y) < 0):
        if telem.time - prev_telem > 15:
            if telem.time - prev_telem > 3:
                customersl.append([telem.time - prev_telem, False])
            if prev_telem - cust_in > 3:
                customersl.append([prev_telem - cust_in, True])
            cust_in = telem.time
    else:
        if (telem.time - prev_telem > 60) or end:
            prev = datetime.fromtimestamp(prev_telem)
            now = datetime.fromtimestamp(telem.time)
            stop_w = prev_telem
            delta = telem.time - prev_telem
            delta_w = stop_w - start_w
            if stop_w - start_w > 3:
                work_time.append([datetime.fromtimestamp(start_w).strftime("%m.%d.%Y, %H:%M:%S"),
                                  datetime.fromtimestamp(stop_w).strftime("%H:%M:%S"),
                                  int(delta_w / 60), delta_w % 60, True, stop_w - start_w])
                work_time.append([prev.strftime("%m.%d.%Y, %H:%M:%S"), now.strftime("%H:%M:%S"),
                                  int(delta / 60), delta % 60, False, telem.time - prev_telem])
            else:
                prev_telem -= work_time[-1][-1]
                prev = datetime.fromtimestamp(prev_telem)
                now = datetime.fromtimestamp(telem.time)
                work_time[-1] = [prev.strftime("%m.%d.%Y, %H:%M:%S"), now.strftime("%H:%M:%S"),
                                  int(delta / 60), delta % 60, False, telem.time - prev_telem]
            start_w = telem.time
            sum_absent += delta
            sum_work += delta_w
    prev_telem = telem.time
    return prev_telem, cust_in, start_w, sum_absent, sum_work, work_time, customersl