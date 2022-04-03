import cv2
import time
import mss
import pyautogui
import numpy as np
import os
import yaml
import random


pyautogui.PAUSE = 0.001
settings = open("settings.yaml", 'r')
s = yaml.safe_load(settings)
# s["screen_area"]["y"]

fps = 0
def printData():
    # return
    mtod = """
        AutoScrap PoA Bot
                                                                 v0.1
        [No toques nada, relájate y disfruta]
        [Cierra esta ventana para parar el bot]
    """
    os.system("cls")
    print(mtod)
    print("Fps:", fps)

def locateAndPlaceWindow():
    ventana = pyautogui.getWindowsWithTitle(s["chrome_location"]["nombre_de_la_ventana"])
    if len(ventana) == 0:
        print ("Ventana del juego no encontrada")
        exit()
    if ventana[0].isMaximized or ventana[0].isMinimized:
        ventana[0].restore()
    ventana[0].moveTo(s["chrome_location"]["x"],s["chrome_location"]["y"])
    ventana[0].resizeTo(s["chrome_location"]["width"],s["chrome_location"]["height"])# w and h, not coordenadas
    ventana[0].activate()
    ventana = pyautogui.getWindowsWithTitle("py.exe")
    if len(ventana) >= 1:
        #ventana[0].minimize()
        ventana[0].moveTo(613,672)
        ventana[0].resizeTo(785,287)

fondo = 0 #1 biblioteca, 2 castillo, 3 comedor
imgFondo = None
fondoLoaded = 0
def loadFondo():
    global fondo
    global fondoLoaded
    if fondo != fondoLoaded:
        string = None
        if fondo == 1:
            string = "img/biblioteca.png"
        elif fondo == 2:
            string = "img/castillo.png"
        elif fondo == 3:
            string = "img/comedor.png"
        global imgFondo
        imgFondo = cv2.imread(string)
        imgFondo = cv2.cvtColor(imgFondo, cv2.COLOR_BGR2GRAY)
        fondoLoaded = fondo

gOffSetY = s["screen_area"]["y"]
gOffSetX = s["screen_area"]["x"]
gWidth = s["screen_area"]["width"]
gHeight = s["screen_area"]["height"]
gMonitorNumber = s["screen_area"]["monitor_number"]
def printScreen(offSetX=0, offSetY=0, maxX=0, maxY=0):
    with mss.mss() as sct:
        global gMonitorNumber
        monitor_number = gMonitorNumber
        mon = sct.monitors[monitor_number]

        # The screen part to capture
        global gOffSetY
        global gOffSetX
        global gWidth
        global gHeight
        width = gWidth
        height = gHeight
        if maxX != 0 and offSetX!=0 and offSetX < maxX:
            width = maxX - offSetX
        if maxY != 0 and offSetY!=0 and offSetY < maxY:
            height = maxY - offSetY
        monitor = {
            "top": mon["top"] + gOffSetY + offSetY,  # 100px from the top
            "left": mon["left"] + gOffSetX + offSetX,  # 100px from the left
            "width": width,
            "height": height,
            "mon": monitor_number,
        }
        image = sct.grab(monitor)
        preArrayNp = np.array(image)
        return preArrayNp[:,:,:3]        

mostradoGUI= False
mostrarGUI= True#s["show_debug_window"]
def mostrarGUIPantalla():
    global mostrarGUI
    global mostradoGUI
    if mostrarGUI and not mostradoGUI:
        mostradoGUI= True
        ventanaGUI = pyautogui.getWindowsWithTitle("AutoScrap PoA Bot")[0]
        ventanaGUI.moveTo(962-8,97)

def writeText(img,x,y,text):
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    coor                   = (x,y)
    fontScale              = 0.35
    fontColor              = (255,0,0)
    thickness              = 1
    lineType               = cv2.LINE_AA

    cv2.putText(img,text, 
    coor, 
    font, 
    fontScale,
    fontColor,
    thickness,
    lineType)

def squareAinsideSquareB(ax,ay,axx,ayy,bx,by,bxx,byy):
    topA=ay
    bottomA=ayy
    rightA=axx
    leftA=ax
    topB=by
    bottomB=byy
    rightB=bxx
    leftB=bx

    if bottomA <= topB:
        return False
    if topA >= bottomB:
        return False
    if rightA <= leftB:
        return False
    if leftA >= rightB:
        return False
    return True

keyPressedLR = False
keyLeft = True
player="Relax"
def pressLeft():
    global keyPressedLR
    global keyLeft
    if keyPressedLR and keyLeft==False:
        pyautogui.keyUp("d")
        pyautogui.keyDown("a")
        keyLeft=True
    elif keyPressedLR==False:
        pyautogui.keyDown("a")
        keyLeft=True
        keyPressedLR=True

def pressRight():
    global keyPressedLR
    global keyLeft
    if keyPressedLR and keyLeft==True:
        pyautogui.keyUp("a")
        pyautogui.keyDown("d")
        keyLeft=False
    elif keyPressedLR==False:
        pyautogui.keyDown("d")
        keyLeft=False
        keyPressedLR=True

cargaCerca=False
cargaX=0
bloqueCerca=False
bloqueX=0
bloqueT=0
playerX=0
lastMove=0
lastMoveIZ=0
def move():
    tm=time.time()*1000
    global player
    global cargaCerca
    global cargaX
    global lastMove
    global bloqueX
    global bloqueCerca
    global playerX
    if bloqueCerca and ((bloqueX-playerX < 200 and bloqueX-playerX>=0) or (playerX-bloqueX < 200 and playerX-bloqueX>=0) ):
        if bloqueX>playerX:
                pressLeft()
        else:
            pressRight()
    elif player=="Relax":
        if cargaCerca==False:
            pressLeft()
        else:
            if cargaX > playerX:
                pressRight()
            else:
                pressLeft()
    elif player=="Carga":
        pressLeft()


def isPlayer(img,x,y,w,h):
    global player
    global cargaCerca
    global cargaX
    global playerX
    if (squareAinsideSquareB(x,y,x+w,y+h,150,338,960,489) and w>77 and w<115 and h>127 and h<139) or (squareAinsideSquareB(x,y,x+w,y+h,150,296,960,492) and w>139 and w<153 and h>175 and h<181):
        if w>77 and w<90:
            writeText(img,x+42,y-12,"Relax")
            writeText(img,x,y-12,"Player")
            player="Relax"
            playerX=x+(w/2)
        else:
            writeText(img,x,y-12,"Player")
            writeText(img,x+42,y-12,"Carga")
            playerX=x+(w/2)
            player="Carga"
        return True
    return False

def isCarga(img,x,y,w,h):
    global cargaCerca
    global cargaX
    # if w>25 and w<49 and h>25 and h<49:
    if w>25 and w<83 and h>25 and h<83:
        writeText(img,x,y-12,"Carga")
        cargaCerca=True
        cargaX=x+(w/2)
        return True
    return False

def isBloque(img,x,y,w,h):
    global bloqueCerca
    global bloqueX
    global bloqueT

    # compareX=0
    # compareY=0
    # if fondo==1:#1 biblioteca, 2 castillo, 3 comedor
    #     compareX,compareY = 0,0
    # elif fondo==2:
    #     compareX,compareY = 0,0
    # elif fondo==3:
    #     compareX,compareY = 0,0

    if (w>90 or h>90) and not (squareAinsideSquareB(x,y,x+w,y+h,150,297,960,492) and w>132 and w<151 and h>78 and h<85) and (y+h)<335:
        writeText(img,x,y-12,"Bomba")
        bloqueCerca=True
        bloqueT=time.time()*1000
        bloqueX=x+(w/2)

        return True
    return False

def processScreenShoot():
    img = printScreen()
    img = cv2.cvtColor(img, cv2.IMREAD_COLOR)
    imgGris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    global imgFondo
    diferencia = cv2.absdiff(imgGris, imgFondo)
    blurred = cv2.GaussianBlur(diferencia, (11,11), 0)
    ret, tframe= cv2.threshold(blurred,0,255,cv2.THRESH_BINARY)
    (cnts, _) = cv2.findContours(tframe.copy(), cv2.RETR_EXTERNAL, 
                             cv2 .CHAIN_APPROX_SIMPLE)
    global mostrarGUI
    global cargaCerca
    cargaCerca=False
    global bloqueCerca
    if mostrarGUI:
        bombas = False
        for cnt in cnts:
            x,y,w,h = cv2.boundingRect(cnt)
            if h < 180:  #Disregard item that are the top of the picture
                if squareAinsideSquareB(x,y,x+w,y+h,0,0,184,550)==False and squareAinsideSquareB(x,y,x+w,y+h,420,0,616,32)==False and squareAinsideSquareB(x,y,x+w,y+h,790,0,951,171)==False and squareAinsideSquareB(x,y,x+w,y+h,156,0,960,491)==True and w>27 and h>27:
                    if not isPlayer(img,x,y,w,h):
                        if not isCarga(img,x,y,w,h):
                            if isBloque(img,x,y,w,h):
                                bombas = True
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                    writeText(img,x,y,""+str(x)+" "+str(y)+" "+str(w)+" "+str(h))
            elif w > 900:
                global stage
                stage = 2
        if bombas== False:
            cond = time.time()*1000-bloqueT
            if cond>150:
                bloqueCerca=False
        move()
        cv2.imshow("AutoScrap PoA Bot", img)
        mostrarGUIPantalla()
        cv2.waitKey(1)

def findImgOnSource(img, source, rango = 0.9 ):
    result = cv2.matchTemplate(source,img,cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= rango:
        return True
    return False

imgBiblioteca = cv2.imread("img/detectLibreria.png")
imgComedor = cv2.imread("img/detectComedor.png")
imgCastillo = cv2.imread("img/detectCastillo.png")
lastTimeCheckedBackGround = 0
def detectFondo():
    source = printScreen()
    global fondo
    global lastTimeCheckedBackGround
    if findImgOnSource(imgBiblioteca,source):
        fondo = 1 #1 biblioteca, 2 castillo, 3 comedor
        loadFondo()
        lastTimeCheckedBackGround= time.time()*1000
        return True
    elif findImgOnSource(imgCastillo,source):
        fondo = 2 #1 biblioteca, 2 castillo, 3 comedor
        loadFondo()
        lastTimeCheckedBackGround= time.time()*1000
        return True
    elif findImgOnSource(imgComedor,source):
        fondo = 3 #1 biblioteca, 2 castillo, 3 comedor
        loadFondo()
        lastTimeCheckedBackGround= time.time()*1000
        return True
    else:
        fondo=0
        return False

def clickVolverAJugar():
    print("disimulando unos segundos..")
    time.sleep(random.randint(2,4))
    pyautogui.moveTo(512+random.randint(0, 30),366+random.randint(0, 5),1/random.randint(80, 120))
    pyautogui.click()
    time.sleep(1/4)

def clickPlayIntro():
    pyautogui.moveTo(473+random.randint(0, 10),474+random.randint(0, 35),1/random.randint(80, 120))
    pyautogui.click()
    time.sleep(1/4)

imgVolverAJugar = cv2.imread("img/volverAJugar.png")
imgPlayIntro = cv2.imread("img/playIntro.png")
stage = 2
def detectStage():
    source = printScreen()
    global stage
    if findImgOnSource(imgVolverAJugar,source):
        stage=3
        print("Escena detectada: volver a jugar")
        time.sleep(1/4)
    elif findImgOnSource(imgPlayIntro,source):
        stage=5
        print("Escena detectada: botón play Intro")
        time.sleep(1/4)
    elif detectFondo()==True:
        stage=1

def dispatcher():
    global stage
    global fondo
    if stage==1: #play
        global lastTimeCheckedBackGround
        condicion = time.time()*1000 - lastTimeCheckedBackGround
        if condicion > 185000:
            detectFondo()
        if fondo != 0:
            processScreenShoot()
    elif stage==2: #stage detection
        fondo = 0
        print("Detectando escena")
        detectStage()
        time.sleep(1/4)
        global keyPressedLR
        pyautogui.keyUp("a")
        pyautogui.keyUp("d")
        global lastMove
        lastMove=0
        playerX=0
        global cargaCerca
        global bloqueCerca
        global bloqueX
        bloqueCerca=False
        bloqueX=0       
        cargaCerca=False
        keyPressedLR=False
    elif stage==3: #stage  play
        clickVolverAJugar()
        stage=2
    elif stage==5: #stage  play Intro
        clickPlayIntro()
        stage=2

def tick():
    printData()
    global fps
    rTime = time.time()*1000
    while True:
        currentTime= time.time()*1000 - rTime
        if currentTime > 1000:
            printData()
            rTime = time.time()*1000
            fps=0
        fps = fps +1
        dispatcher()

def main():
    locateAndPlaceWindow()
    tick()

if __name__ == '__main__':
    main()