import numpy as np
import cv2
import random
from imutils.object_detection import non_max_suppression
# from imutils import paths
import imutils
import cv2
from .models import Telemetry
# from ..cofe_telemetry.settings import MEDIA_ROOT

#default HOG
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

print('я здесь')


def tracker(cap):
    ret, img = cap.read()
    cadr = 1
    start_time = Telemetry.objects.first().time
    f_width = 400 / img.shape[0]
    while True:
        ret, img = cap.read()
        cadr += 1

        if ret == False:
            break

        img = imutils.resize(img, width = 400)
        # print(Telemetry.objects.filter(time=cadr*15+start_time).first())
        # break
        coord = Telemetry.objects.filter(time=start_time+int(cadr/15)).order_by('-detectionProbability').first()
        if coord:
            coord = coord.detectionCoordinates
        else:
            coord = {"x1":0,"y1":0,"x2":1,"y2":1}
        print(coord)
        rects = np.array([[coord['x1']*f_width, coord['y1']*f_width, coord['x2']*f_width, coord['y2']*f_width]])
        # find largest possible rectangel to avoid detection
        # of same person several times
        biggest = non_max_suppression(rects, probs=None, overlapThresh=0.65)

        # draw largest rectangle
        for (xA, yA, xB, yB) in biggest:
            # create random color
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            cv2.rectangle(img, (xA, yA), (xB, yB), color, 2)

            # show image
        cv2.imshow('Image', img)
        # ret, jpeg = cv2.imencode('.jpg', img)
        k = cv2.waitKey(30) & 0xFF
        if k == 27:
            break

        # return jpeg.tobytes()
# run video
cap = cv2.VideoCapture('media/12_апр.,_21_44_27_12_апр.,_22_53_36___1e33f690.mp4')
tracker(cap)
# release frame and destroy windows
cap.release()
cv2.destroyAllWindows