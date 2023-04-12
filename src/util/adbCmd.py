#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import random
import re
import subprocess
import time


def screenshot(serial, filename):
    os.system(f'adb -s {serial} shell screencap -p /sdcard/screen.jpg')
    os.system(f'adb -s {serial} pull /sdcard/screen.jpg {filename}')


def click_button(serial, x1, x2, y1, y2):
    x, y = random.randint(x1, x2), random.randint(y1, y2)
    result = subprocess.run(f'adb -s {serial} shell input tap {x} {y}', shell=True)
    time.sleep(1)
    if result.returncode:
        return False, result.stdout
    return True, ''


def input_text(serial, text):
    result = subprocess.run(f'adb -s {serial} shell am broadcast -a ADB_INPUT_TEXT --es msg {text}', shell=True)
    if result.returncode:
        return False, result.stdout
    return True, ''


def start_app(package, activity, serial):
    result = subprocess.run(f'adb -s {serial} shell am start -n {package}/{activity}', shell=True, stdout=subprocess.PIPE)
    if result.returncode:
        return False, result.stdout
    return True, ''


def install_apk(serial, apk, package):
    result = subprocess.run(f'adb -s {serial} shell pm list packages | grep "{package}"', shell=True, stdout=subprocess.PIPE)
    if result.stdout != b'':
        return True, ''

    result = subprocess.run(f'adb -s {serial} install {apk}', shell=True, stdout=subprocess.PIPE)
    if result.returncode:
        return False, result.stdout
    return True, ''


def enable_apk(serial, activity):
    result = subprocess.run(f'adb  -s {serial} shell ime enable {activity}', shell=True, stdout=subprocess.PIPE)
    if result.returncode:
        return False, result.stdout
    return True, ''


def setting_apk(serial, ime):
    result = subprocess.run(f'adb  -s {serial} shell ime set {ime}', shell=True, stdout=subprocess.PIPE)
    if result.returncode:
        return False, result.stdout
    return True, ''


# 获取屏幕尺寸，返回height， width
def get_wm_size(serial):
    result = subprocess.run(f'adb -s {serial} shell wm size', shell=True, stdout=subprocess.PIPE)
    if result.returncode != 0:
        return 0, 0

    pattern = re.compile('[\d+]+')
    sizes = pattern.findall(result.stdout.decode())
    if len(sizes) != 2:
        return 0, 0
    return sizes[0], sizes[1]


def check_device_available(serial):
    result = subprocess.run(f'adb devices | grep {serial}', shell=True, stdout=subprocess.PIPE)
    if result.returncode != 0:
        return []

    if result.stdout == b'':
        return False
    return True
