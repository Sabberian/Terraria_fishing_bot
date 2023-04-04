import time
from datetime import datetime
import keyboard
from ctypes import windll, Structure, c_long, byref
from time import sleep
import cv2
import mss
import numpy as np
import pyautogui as pg
import pytesseract
import os

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def get_mouse_position():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return {'x': pt.x, 'y': pt.y}

def screenshot(bbox):
    if bbox:
        img = np.asarray(sct.grab(bbox))
    else:
        mon = sct.monitors[0]
        bbox = (mon["left"], mon["top"], mon["left"] + mon["width"], mon["top"] + mon["height"])
        img = np.asarray(sct.grab(bbox))
    return img

def click():
    pg.mouseDown()
    sleep(0.01)
    pg.mouseUp()

def press(k):
    pg.keyDown(str(k))
    sleep(0.01)
    pg.keyUp(str(k))

def right_click():
    pg.mouseDown(button="right")
    sleep(0.01)
    pg.mouseUp(button="right")

def get_chests_coords(screenshot):
    chests_path = list(os.listdir('chests'))
    chest_imgs = []
    gray_scr = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    cc = []
    for c in chests_path:
        template = cv2.cvtColor(cv2.imread('chests/' + c), cv2.COLOR_BGR2GRAY)
        chest_imgs.append(template)
        h, w = template.shape
        res = cv2.matchTemplate(gray_scr, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(min_val, max_val, min_loc, max_loc)
        mid = (max_loc[0] + w // 2, max_loc[1] + h // 2)
        if max_val > 0.6:
            cc.append(mid)
    print(cc)
    return cc

def put_items(screenshot, m_cord):
    cc = get_chests_coords(screenshot)
    if cc:
        for cord in cc:
            pg.moveTo(cord)
            sleep(0.3)
            right_click()
            sleep(0.5)
            pg.keyDown('shift')
            start_pos = (60, 125)
            for i in range(10):
                for j in range(4):
                    pg.moveTo(start_pos[0] + i*70, start_pos[1] + j*70)
                    sleep(0.1)
                    click()
            pg.keyUp('shift')
            press('esc')
            sleep(0.5)
            pg.moveTo(m_cord)
            sleep(1)


if __name__ == '__main__':
    avalible_drop = ['железный ящик', 'деревянный ящик', 'океанический ящик', 'розовая медуза', 'золотой ящик',
                     'тунец', 'красный луциан', 'рыба-бомба', 'креветка']
    title = "Terraria fishing"
    is_working = True


    sct = mss.mss()
    print('[!]Started: 10 seconds to preparation...')
    sleep(5)
    for i in range(5):
        print(5 - i)
        sleep(1)
    
    print('[!]Started')
    last_putting_time = time.time()
    last_drink_time = time.time()
    print('Drinking potion')
    press(9)
    click()
    sleep(0.2)
    press(2)
    click()
    print('Fishing')    

    while True:
        if is_working:
            mouse_pos = get_mouse_position()
            left, top = mouse_pos['x'] - 50, mouse_pos['y'] - 50
            
            bbox = {'top' : top, 'left': left, 'width': 100, 'height': 100}

            img = screenshot(bbox)

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_yellow = np.array([22, 93, 0])
            upper_yellow = np.array([45, 255, 255])
            mask0 = cv2.inRange(hsv, lower_yellow, upper_yellow)
            

            lower_yellow = np.array([192, 93, 0])
            upper_yellow = np.array([215, 255, 255])
            mask1 = cv2.inRange(hsv, lower_yellow, upper_yellow)

            mask = mask0 + mask1

            res = cv2.bitwise_and(img, img, mask=mask)
            cv2.imshow(title, res)
            
            # print(np.sum(mask))
            if np.sum(mask) < 700:
                sleep(0.1)
                print(datetime.now().strftime("%H:%M:%S"), 'Caught!')
                click()

                time.sleep(0.3)
                print()
                print(datetime.now().strftime("%H:%M:%S"), 'New attemp')
                if time.time() - last_drink_time > 60 * 8:
                    print(datetime.now().strftime("%H:%M:%S"), 'Drinking potion')
                    press(9)
                    click()
                    sleep(0.2)
                    last_drink_time = time.time()
                    press(2)
                else:
                    print(datetime.now().strftime("%H:%M:%S"), 'Potion is still affecting you')
                
                if time.time() - last_putting_time > 60 * 15:
                # if time.time() - last_putting_time > 20:
                    print(datetime.now().strftime("%H:%M:%S"), 'Putting items in chest')
                    mp = get_mouse_position()
                    put_items(screenshot(None), (mp['x'], mp['y']))
                    last_putting_time = time.time()

                click()
                sleep(1)
        if keyboard.is_pressed('q'):
            is_working = not is_working
            if not is_working:
                print(datetime.now().strftime("%H:%M:%S"), 'stopped')
                sleep(3)
            else:
                print(datetime.now().strftime("%H:%M:%S"), 'started')
                sleep(3)
        