'''TODO
1) 이미지 Load
    - 이미지를 선택하여 화면에 나타낸다
    - 이미지는 1080 * 1920의 크기에 맞추어야 한다.
2) 이미지상 구역설정
    - 3각 또는 4각형 지정 (RT, LT, RB, LB)
3) 저장시 사이트 ID, 디바이스 ID, 구역 유형 지정
    - 사이트 아이디: 입력가능하도록(대상의 경우는 220901)
    - 디바이스 아이디: DB연동의 경우 tbvision_device에서 조회후 선택, 그외 입력
    - 구역 유형: 3가지 값이 있는 selectbox
4) 데이터베이스 연동
    - postgresql DB 연동
    - Vision Device 조회(tbvision_device)
    - 예외구역 조회 및 저장(tbvision_except_region)
5) 데이터베이스 연동이 안 되는 경우 파일로 설정 저장
'''

import cv2
import numpy as np
import psycopg2
import os
import json

from vals import setcoordinates
from conDB import *

# Import Tkinter
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

connect()
create_table()

''' DB연결 실패할 경우 대비 json파일 생성 '''
try:
    with open('data.json', 'r') as rf:
        exist = json.load(rf)
except:
    newJson = {"DB_Data":[]}
    json_obj = json.dumps(newJson, indent=4)
    with open("data.json", "w") as outfile:
        outfile.write(json_obj)

#Create an instance of Tkinter frame
win= Tk()
win.title("대상LS 예외구역 설정 Tool")
#Set the geometry of Tkinter frame
win.geometry("710x200")

# returns is value is None or not
def isEmpty(value):
    return value == None

''' From here is image processing by opencv'''
coord_list = []
temp = []
resultInsertData = []
drawData = []
def processImg(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, (540, 960))

    global coord_list
    global temp
    global resultInsertData
    global drawData

    if isEmpty(coord_list) != True:
        coord_list = []
        resultInsertData = []
        temp = []
        drawData = []

    def click_event(event, x, y, flags, param):
        # checking for left mouse clicks
        # 클릭하여 좌표지정
        global coord_list
        global temp
        global line_color

        if flags & cv2.EVENT_FLAG_SHIFTKEY:
            line_color = (0, 0, 255)
            if event == cv2.EVENT_RBUTTONDOWN:
                temp = []
        else:
            line_color = (0, 255, 0)

        if event == cv2.EVENT_LBUTTONDOWN:
            # displaying the coordinates on the Shell
            coord_list.append([x * 2, y * 2])
            temp.append([x, y])

        if event == cv2.EVENT_RBUTTONDOWN:
            if temp != None:
                coord_list = coord_list[:len(coord_list) - 1]
                temp = temp[:len(temp) - 1]

    # Display the image
    cv2.namedWindow("image")
    cv2.imshow("image", img)
    cv2.setMouseCallback('image', click_event)
    global line_color
    line_color = (0, 255, 0)

    # Wait until the user closes the window
    while True:
        cv2.imshow("image", img)

        img_copy = img.copy()
        for i in range(len(temp)):
            cv2.circle(img_copy, temp[i], 1, (255, 255, 0), 5)

        for d in drawData:
             cv2.polylines(img_copy, np.int32([d]), True, (0, 255, 0), 2)

        cv2.polylines(img_copy, np.int32([temp]), True, line_color, 2)
        cv2.imshow("image", img_copy)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cv2.destroyWindow("image")
            cVLEntry.delete(0, END)
            coordinates = setcoordinates(resultInsertData)
            cVLEntry.insert(0, coordinates)
            break
        elif key == ord("s"):
            resultInsertData.append(coord_list)
            drawData.append(temp)
            coord_list = []
            temp = []

modtemp = []
resultModifyData = []
drawModifyData = []
def modifyImg(image_path, pnt_datas):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, (540, 960))
    cVLEntry.delete(0, END)

    global coord_list
    global modtemp
    global resultModifyData
    global drawModifyData

    if isEmpty(coord_list) != True:
        coord_list = []
        resultModifyData = []
        modtemp = []
        drawModifyData = []

    for shape in pnt_datas:
        t = []
        for pnt in shape:
            t.append([int(pnt[0] / 2), int(pnt[1] / 2)])
        drawModifyData.append(t)

    global ismodtempClear
    ismodtempClear = False

    # 불러온 좌표의 박스 좌표 계산
    global shapes
    shapes = []
    for shape in drawModifyData:
        xlist = []
        ylist = []
        for pnt in shape:
            xlist.append(pnt[0])
            ylist.append(pnt[1])
        xmin = min(xlist)
        xmax = max(xlist)
        ymin = min(ylist)
        ymax = max(ylist)
        shapes.append((xmin, ymin, xmax, ymax))

    def click_event(event, x, y, flags, param):
        # checking for shift input
        # shift키 누르면 지정좌표 색바꿈
        global coord_list
        global line_color
        global modtemp
        global ismodtempClear
        global drawModifyData
        global shapes
        global resultModifyData

        for i, (xmin, ymin, xmax, ymax) in enumerate(shapes):
            if flags & cv2.EVENT_FLAG_SHIFTKEY and event == cv2.EVENT_RBUTTONDOWN:
                if x >= xmin and x <= xmax and y >= ymin and y <= ymax:
                    del drawModifyData[i]
                    del shapes[i]
                    if len(drawModifyData) != 0:
                        for shape in drawModifyData:
                            temp = []
                            for pnt in shape:
                                temp.append([pnt[0] * 2, pnt[1] * 2])
                            resultModifyData.append(temp)
                    else:
                        drawModifyData = []
                        resultModifyData = []

                    ismodtempClear = True
                else:
                    line_color = (0, 255, 0)
            else:
                line_color = (0, 255, 0)
        
        if ismodtempClear:
            if event == cv2.EVENT_LBUTTONDOWN:
                # displaying the coordinates on the Shell
                coord_list.append([x * 2, y * 2])
                modtemp.append([x, y])

            if event == cv2.EVENT_RBUTTONDOWN:
                if modtemp != None:
                    coord_list = coord_list[:len(coord_list) - 1]
                    modtemp = modtemp[:len(modtemp) - 1]

    # Display the image
    cv2.imshow("image", img)
    cv2.setMouseCallback('image', click_event)
    global line_color
    line_color = (0, 255, 0)
    
    while True:
        cv2.imshow("image", img)
        
        img_copy = img.copy()
        if modtemp != []:
            for i in range(len(modtemp)):
                cv2.circle(img_copy, modtemp[i], 1, (255, 255, 0), 5)

        for d in drawModifyData:
             cv2.polylines(img_copy, np.int32([d]), True, line_color, 2)

        cv2.polylines(img_copy, np.int32([modtemp]), True, line_color, 2)
        cv2.imshow("image", img_copy)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cv2.destroyAllWindows()
            break
        elif key == ord("s"):
            resultModifyData.append(coord_list)
            drawModifyData.append(modtemp)
            coord_list = []
            modtemp = []
            
def openDrawImg():
    global coord_list
    global temp
    global isUpdate

    rTPCombo.set("예외구역유형 선택")
    if isEmpty(imgPathEntry) != True:
        imgPathEntry.delete(0, END)
        imgPathEntry.insert(0, "")
    if isEmpty(cVLEntry) != True:
        cVLEntry.delete(0, END)
        cVLEntry.insert(0, "좌표 값")
    if isEmpty(dIDEntry) != True:
        dIDEntry.delete(0, END)
        dIDEntry.insert(0, "기기ID")

    # Read from files
    path = askopenfilename()
    if path != '':
        print("user chose", path)
        imgPathEntry.insert(0, path)
        processImg(path)

        isUpdate = False
    else:
        print("Image Not Selected")
''' End of Opencv processing '''

def saveBtn():
    global isUpdate
    if isUpdate:
        update_data(cVLvalue.get(), sIDvalue.get(), dIDvalue.get(), rTPCombo.get(), imgPathEntry.get())
    else:
        insert_data(sIDvalue.get(), dIDvalue.get(), rTPCombo.get(), cVLEntry.get(), imgPathEntry.get())
        messagebox.showinfo(title="Save Data Success", message="INSERT INTO config_values: SUCCESS")
        
    # 좌표값, 파일 경로가 값이 있는 상태면 초기화
    rTPCombo.set("예외구역유형 선택")
    if isEmpty(imgPathEntry) != True:
        imgPathEntry.delete(0, END)
        imgPathEntry.insert(0, "")
    if isEmpty(cVLEntry) != True:
        cVLEntry.delete(0, END)
        cVLEntry.insert(0, "좌표 값")
    if isEmpty(dIDEntry) != True:
        dIDEntry.delete(0, END)
        dIDEntry.insert(0, "기기ID")

def deleteBtn():
    delete_data(sIDvalue.get(), dIDvalue.get(), rTPCombo.get())
    rTPCombo.set("예외구역유형 선택")
    if isEmpty(dIDEntry) != True:
        dIDEntry.delete(0, END)
        dIDEntry.insert(0, "기기ID")

modify_row_data = None
isUpdate = False
def updateBtn():
    global isUpdate
    global resultModifyData
    isUpdate = True

    if isCon() == False:
        messagebox.showwarning(title="DB Connection FAIL", message="DB Connection FAIL: 데이터를 불러올 수 없음")


    modify_row_data = select_row(sIDvalue.get(), dIDvalue.get(), rTPCombo.get())
    if modify_row_data != None:
        # Read from files
        mod_imgPath = askopenfilename()
        if mod_imgPath != '':
            print("user chose", mod_imgPath)
            imgPathEntry.insert(0, mod_imgPath)

            # tempdata는 길이가 1인 string 좌표
            shapes = []
            if modify_row_data != None:
                tempdata = modify_row_data[3]
                if ':' in tempdata:
                    tempdata = modify_row_data[3].split(" : ")
                else:
                    tempdata = modify_row_data[3].split(", ")
                
                for tmp in tempdata:
                    each = tmp.split(", ")
                    pnts = []
                    for e in each:
                        X = int(e.split(',')[0])
                        Y = int(e.split(',')[1])
                        pnts.append([X, Y])
                    shapes.append(pnts)
            
                modifyImg(mod_imgPath, shapes)
                coordinates = setcoordinates(resultModifyData)
                cVLEntry.insert(0, coordinates)
        else:
            print("Image Not Selected")
    else:
        messagebox.showwarning(title="No data in data.json", message="NO DATA FAILURE: 새 데이터를 추가하세요.")

if __name__ == "__main__":
    baserow = 0

    ''' Image Load Part '''
    imgPathEntry = Entry(win, width=60)
    imgPathEntry.grid(row=baserow+1, column=1, columnspan=3, padx=10)
    Button(text="이미지 불러오기", width=15, command=openDrawImg).grid(row=baserow+1, column=0, padx=10, pady=5)
    ''' Image Load Part End '''

    ''' Informations Part '''
    site_id = Label(win, text="Site ID", font=('Arial', 10))
    device_id = Label(win, text="Device ID", font=('Arial', 10))
    reg_type = Label(win, text="Reg Type", font=('Arial', 10))
    cIDvalue = Label(win, text="Coordinates", font=('Arial', 10))

    site_id.grid(row=baserow+2, pady=5)
    device_id.grid(row=baserow+3, pady=5)
    reg_type.grid(row=baserow+4, pady=5)
    cIDvalue.grid(row=baserow+5, pady=5)

    sIDvalue = StringVar(win, value="220901")
    dIDvalue = StringVar(win, value="기기ID")
    cVLvalue = StringVar(win, value="좌표 값")

    sIDEntry = Entry(win, width=18, textvariable = sIDvalue)
    dIDEntry = Entry(win, width=18, textvariable = dIDvalue)
    cVLEntry = Entry(win, width=76, textvariable = cVLvalue)
    
    rTPCombo = ttk.Combobox(win, width=15, height=5, values=[0, 1, 2])
    rTPCombo.set("예외구역유형 선택")

    sIDEntry.grid(row=baserow+2, column=1)
    dIDEntry.grid(row=baserow+3, column=1)
    rTPCombo.grid(row=baserow+4, column=1)
    cVLEntry.grid(row=baserow+5, column=1, columnspan=4)
    ''' Informations Part End'''

    ''' Save Button '''
    Button(text="저장", width=15, command=saveBtn).grid(row=baserow+1, column=4)
    
    ''' Delete Button '''
    Button(text="삭제", width=15, command=deleteBtn).grid(row=baserow+2, column=4)
    
    ''' Find Data Button '''
    Button(text="불러오기", width=15, command=updateBtn).grid(row=baserow+3, column=4)

    win.mainloop()
