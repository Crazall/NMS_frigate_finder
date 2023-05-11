import win32gui
import win32ui
from PIL import Image
import ctypes


def catchScreen(screenRegion,windowClass,windowTitle,toPath):
        
    # 获取窗口句柄
    #hwnd = win32gui.FindWindow('GLFW30', "No Man's Sky")
    hwnd = win32gui.FindWindow(windowClass, windowTitle)
    # 获取截图位置和大小
    left, top, width, height = screenRegion[0], screenRegion[1], screenRegion[2], screenRegion[3]
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
    img.save(toPath)

