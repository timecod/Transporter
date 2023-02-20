import cv2
import numpy as np
from imutils.video import VideoStream
import imutils
from time import sleep
import RPi.GPIO as GPIO

class Low_osi:
    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([11, 12, 13], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup([3, 5], GPIO.OUT, initial=GPIO.HIGH)

    def move (self, L, R):
        GPIO.output(5, L == 0)
        GPIO.output(3, R == 0)
        GPIO.output(12, R > 0)
        GPIO.output(13, L > 0)

    def trap(self, flag):
        GPIO.output(11, flag)

    def end(self):
        GPIO.cleanup()

class Transport:
    def __init__ (self, osi):
        self.x = 0
        self.y = 0
        self.ang = 0
        self.trapp = False
        self.osi = osi

    def right_rotate (self):
        osi.move(1, -1)
        sleep(0.1)
        self.ang -= 0.17

    def left_rotate (self):
        osi.move(-1, 1)
        sleep(0.1)
        self.ang += 0.17

    def forward (self):
        osi.move(1, 1)
        sleep(0.1)
        self.y += np.sin(self.ang)*5
        self.x += np.cos(self.ang)*5

    def back (self):
        osi.move(-1, -1)
        sleep(0.1)
        self.y -= np.sin(self.ang)*5
        self.x -= np.cos(self.ang)*5

    def stop (self):
        osi.move(0, 0)

    def grab (self):
        self.trapp = not self.trapp
        osi.trap(self.trapp)

    def rotate_full (self):
        self.ang += np.pi
        r = 2*(self.ang > 0) - 1
        osi.move(r, -1*r)
        sleep(0.1/0.17*np.pi)

BRAKE_COLOR = [[101, 200, 128], [121, 255, 255], "BRAKE"]
RED_COLOR = [[165, 200, 175], [185, 255, 255], "RED"]
BLUE_COLOR = [[79, 200, 175], [99, 255, 255], "BLUE"]
BLACK_COLOR = [[0, 5, 50], [179, 50, 128], "BLACK"]

class Camera:
    def __init__ (self, frameSize):
        self.size = list(frameSize)
        self.vs = VideoStream(src=0, usePiCamera=True, resolution=frameSize, framerate=32).start()
        sleep(2)
        self.get_img()
    def get_img(self):
        self.img = cv2.medianBlur(self.vs.read(), 7)
        self.hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    def get_countour(self, color):
        cv2.inRange(self.hsv, np.array(color[0]), np.array(color[1]))
        bit = cv2.bitwise_and(self.img, self.img, mask=b)
        gray = cv2.cvtColor(bit, cv2.COLOR_BGR2GRAY)
        countours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(countours) != 0:
            c = max(countours, key = cv2.contourArea)
            x,y,w,h = cv2.boundingRect(c)

            # если прямоугольник достаточного размера...
            if w*h>500:

                return [x + w/2, y + h/2, w*h]
        return None
    def get_ang(self, countour):
        max_ang = 72/2/180*np.pi
        x_n = -1*(countour[0] - self.size[0]/2)
        ang = x_n / (self.size[0]/2) * max_ang
        return ang
    def get_r(self, countour):
        if countour[2] > 30000:
            return 0
        return (self.size[1] * 3 / 4) / countour[1] * 10
    def show(self, wname):
        cv2.imshow(wname, self.img)
    def draw(self, countour):
        cv2.circle(self.img, (countour[0], countour[1]), np.sqrt(countour[2]/np.pi), (0, 255, 0), thickness=2, lineType=8, shift=0)
    def stop(self):
        self.vs.stop()

WNAME = "Tranporter"
cam = Camera((640, 480))
osi = Low_osi()
transp = Transport(osi)
colors = [BLACK_COLOR, BLUE_COLOR, RED_COLOR, BRAKE_COLOR]
color_cube = None
in_zone = False
def do_avoid(cont, color):
    global cam, transp
    if color == "BRAKE" and cam.get_r(cont) <= 20:
        cam.draw(cont)
        transp.stop()
        while abs(cam.get_ang()) <= 20/180*np.pi:
            if cam.get_ang() > 0:
                transp.right_rotate()
            else:
                transp.left_rotate()
        transp.forward()
        transp.stop()

def do_gift(cont, color):
    global cam, transp, color_cube
    if color == color_cube and cam.get_r(cont) >= 50:
        cam.draw(cont)
        transp.forward()
        if cam.get_ang() < -10:
            transp.right_rotate()
        if cam.get_ang() > 10:
            transp.left_rotate()
        if cam.get_r(cont) < 50:
            for i in range(10):
                transp.forward()
            transp.stop()
            color_cube = None
            transp.grab()
            for i in range(5):
                transp.back()
            transp.rotate_full()
            transp.stop()
def do_search_zone(cont, color):
    global cam, transp, color_cube
    if color == "BLACK" and color_cube == None and cam.get_r(cont) >= 20:
        cam.draw(cont)
        transp.forward()
        if cam.get_ang() < -10:
            transp.right_rotate()
        if cam.get_ang() > 10:
            transp.left_rotate()
    if color == "BLACK" and color_cube == None and cam.get_r(cont) < 20:
        transp.right_rotate()
def do_search_cube(cont, color):
    global cam, transp, color_cube
    if (color == "RED" or color == "BLUE") and color_cube == None and cam.get_r(cont) >= 20 and cam.get_r(cont) < 50:
        color_cube = color
    if color == color_cube and cam.get_r(cont) >= 20 and cam.get_r(cont) < 50:
        cam.draw(cont)
        transp.forward()
        if cam.get_ang() < -10:
            transp.right_rotate()
        if cam.get_ang() > 10:
            transp.left_rotate()
        if cam.get_r(cont) < 20:
            for i in range(5):
                transp.forward()
            transp.stop()
            transp.grab()
            transp.forward()
            transp.grap()
            sleep(0.1)
            transp.grap()
            sleep(0.1)
            transp.rotate_full()
            transp.stop()
if __name__ == "__main__":
    cv2.namedWindow(WNAME)
    cv2.resizeWindow(WNAME, 640, 480)
    osi.setup()
    try:
        while True:
            if color_cube != None:
                for color in colors[1:]:
                    cont = cam.get_countour(color)
                    if cont != None:
                        do_avoid(cont, color)
                        do_gift(cont, color)
            else:
                for color in colors:
                    cont = cam.get_countour(color)
                    if cont != None:
                        do_avoid(cont, color)
                        do_search_cube(cont, color)
                        do_search_black(cont, color)
            cam.show(WNAME)
            k = cv2.waitKey(1)
            if k == 27:
                move(0,0)
                end()
                cv2.destroyAllWindows()
                vs.stop()
                break
    except KeyboardInterrupt:
        osi.end()
        cv2.destroyAllWindows()
        cam.stop()

