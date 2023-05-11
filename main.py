import pyautogui
import cv2
import time
import keyboard
import winsound
import os
import numpy as np
import win32gui
import win32ui
from PIL import Image
import ctypes

# 系统提示音的频率和持续时间
duration = 300  # millisecond
freq = 1000  # Hz

debug = True  # 调试模式，保存每一次截图的副本

similarityThreshold = 0.2  # 相似度的阈值

checkSlice = 2  # 两次检查之间的时间间隔，以秒为单位

timeToAddFuel = 120  # 添加脉冲驱动器的燃料的时间间隔，以秒为单位

stopShipKey = 's'  # 停止脉冲的按键，默认为s键

confirmKey = 'w'  # 确认的按键，如果找到了船但是没有按确认按键就一直滴滴滴

addFuelKey = '9'  # 给脉冲驱动器充能的快捷键

filePath = 'c:/Users/Joseph/Desktop/xgj/无人深空寻找生物护卫舰小帮手/'  # 文件夹的名字，结尾处有'/'符号

screenshotRegion = (3557, 1679, 65, 85)  # 截取右下角图标的区域，用于探测是否有鲸鱼之歌图标

screenWidth, screenHeight = 3840, 2160

foundIconImg = cv2.imdecode(np.fromfile(os.path.join(filePath + '鲸鱼之歌图标图片.png'), dtype=np.uint8),
                            0)  # 出现鲸鱼之歌时的图标图片


def catchScreen(windowWidth, windowHeight, screenShotRegion, windowClass, windowTitle,
                toPath):  # 获取后台窗口画面的函数，本来想做一个后台挂着的脚本，但是由于无人深空后台挂着就暂停而作罢...

    # 获取窗口句柄
    hwnd = win32gui.FindWindow(windowClass, windowTitle)
    # 获取截图位置和大小
    width, height = windowWidth, windowHeight
    # 获取窗口DC
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

    # 将位图选入到DC对象中
    saveDC.SelectObject(saveBitMap)

    # 将窗口DC中的内容拷贝到saveDC中
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)

    # 获取位图信息
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    # 将位图信息转换成PIL Image对象
    img = Image.frombuffer(
        "RGB",
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr,
        "raw",
        "BGRX",
        0,
        1
    )

    # 保存图像
    img.crop((screenShotRegion[0], screenShotRegion[1], screenShotRegion[0] + screenShotRegion[2],
              screenShotRegion[1] + screenShotRegion[3])).save(toPath)


def checkIcon():  # 检查屏幕的截图范围内是否包含鲸鱼之歌图标图片
    pyautogui.screenshot(region=screenshotRegion).save(filePath + 'temp.png')
    currentImg = cv2.imdecode(np.fromfile(os.path.join(filePath + 'temp.png'), dtype=np.uint8), 0)
    similarity = cv2.minMaxLoc(cv2.matchTemplate(currentImg, foundIconImg, cv2.TM_SQDIFF_NORMED))[
        0]  # 相似度，取值于0,1之间，越靠近0表示越相似
    print('当前相似度【{0:.3f}】'.format(similarity))
    return similarity < similarityThreshold


def checkAndSaveIcon():
    localTime = time.localtime()
    try:
        pyautogui.screenshot(region=screenshotRegion).save(
            filePath + time.strftime("%Y-%m-%d/%H时%M分%S秒", localTime) + '.png')
    except FileNotFoundError:
        os.mkdir(filePath + time.strftime("%Y-%m-%d", localTime))
        pyautogui.screenshot(region=screenshotRegion).save(
            filePath + time.strftime("%Y-%m-%d/%H时%M分%S秒", localTime) + '.png')
        print(time.strftime("%Y-%m-%d", localTime) + '文件夹不存在，已创建新文件夹')
    currentImg = cv2.imdecode(
        np.fromfile(os.path.join(filePath + time.strftime("%Y-%m-%d/%H时%M分%S秒", localTime) + '.png'),
                    dtype=np.uint8), 0)
    similarity = cv2.minMaxLoc(cv2.matchTemplate(currentImg, foundIconImg, cv2.TM_SQDIFF_NORMED))[
        0]  # 相似度，取值于0,1之间，越靠近0表示越相似
    print('当前相似度【{0:.3f}】'.format(similarity))
    if similarity < similarityThreshold:
        os.rename(filePath + time.strftime("%Y-%m-%d/%H时%M分%S秒", localTime) + '.png',
                  filePath + time.strftime("%Y-%m-%d/%H时%M分%S秒【{0:.3f}】".format(similarity), localTime) + '.png')
    else:
        os.rename(filePath + time.strftime("%Y-%m-%d/%H时%M分%S秒", localTime) + '.png',
                  filePath + time.strftime("%Y-%m-%d/%H时%M分%S秒({0:.3f})".format(similarity), localTime) + '.png')
    return similarity < similarityThreshold


def confirm():
    while True:
        winsound.Beep(freq, duration)
        if keyboard.is_pressed('w'):
            break
        time.sleep(0.5)


def normalMode():
    notice='【正常模式】'
    startTime = time.time()
    while True:
        if checkIcon():
            # 释放提示音并按下s键停止脉冲
            winsound.Beep(freq, duration)
            winsound.Beep(freq, duration)
            winsound.Beep(freq, duration)
            keyboard.press(stopShipKey)
            time.sleep(0.5)
            keyboard.release(stopShipKey)
            confirm()
            break
        print(notice+'\n当前充能循环已运行{0:.1f}秒'.format(time.time()-startTime)+'\n---------------------')
        winsound.Beep(int(freq / 3), int(duration))  # 运行提示音
        if time.time() - startTime > timeToAddFuel:
            # 添加脉冲驱动器燃料
            keyboard.press(addFuelKey)
            time.sleep(0.5)
            keyboard.release(addFuelKey)
            time.sleep(0.5)
            pyautogui.mouseDown(button='right')
            time.sleep(0.5)
            pyautogui.mouseUp(button='right')
            time.sleep(0.5)
            pyautogui.mouseDown(button='right')
            time.sleep(0.5)
            pyautogui.mouseUp(button='right')
            # 重置计时器
            startTime = time.time()
        time.sleep(checkSlice)


def debugMode():
    notice='【调试模式】'
    startTime = time.time()
    while True:
        if checkAndSaveIcon():
            # 释放提示音并按下s键停止脉冲
            winsound.Beep(freq, duration)
            winsound.Beep(freq, duration)
            winsound.Beep(freq, duration)
            keyboard.press(stopShipKey)
            time.sleep(0.5)
            keyboard.release(stopShipKey)
            confirm()
            break
        print(notice+'\n当前充能循环已运行{0:.1f}秒'.format(time.time()-startTime)+'\n---------------------')
        winsound.Beep(int(freq / 3), int(duration))  # 运行提示音
        if time.time() - startTime > timeToAddFuel:
            # 添加脉冲驱动器燃料
            keyboard.press(addFuelKey)
            time.sleep(0.5)
            keyboard.release(addFuelKey)
            time.sleep(0.5)
            pyautogui.mouseDown(button='right')
            time.sleep(0.5)
            pyautogui.mouseUp(button='right')
            time.sleep(0.5)
            pyautogui.mouseDown(button='right')
            time.sleep(0.5)
            pyautogui.mouseUp(button='right')
            # 重置计时器
            startTime = time.time()
        time.sleep(checkSlice)


if __name__ == '__main__':
    if debug:
        debugMode()
    else:
        normalMode()
    # catchScreen(screenWidth,screenHeight,screenshotRegion,'GLFW30', "No Man's Sky", filePath+'TESTPNG.png')
