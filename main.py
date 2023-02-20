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
import vals
from conDB import *

# Import Tkinter
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

import keyboard

work = vals.SpacePos()
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
win.geometry("450x400")

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
    imgPathEntry.insert(0, image_path)
    uVLEntry.delete(0, END)

    global coord_list
    global modtemp
    global resultModifyData
    global drawModifyData
    if isEmpty(coord_list) != True:
        coord_list = []

    for shape in pnt_datas:
        t = []
        for pnt in shape:
            t.append([pnt[0] / 2, pnt[1] / 2])
        drawModifyData.append(t)

    global ismodtempClear
    ismodtempClear = False

    def click_event(event, x, y, flags, param):
        # checking for shift input
        # shift키 누르면 지정좌표 색바꿈
        global coord_list
        global line_color
        global modtemp
        global ismodtempClear
        global drawModifyData

        if flags & cv2.EVENT_FLAG_SHIFTKEY:
            line_color = (0, 0, 255)
            if event == cv2.EVENT_RBUTTONDOWN:
                drawModifyData = []
                ismodtempClear = True
        else:
            line_color = (0, 255, 0)

        if len(drawModifyData) != 0:
            pass
        else:
            drawModifyData = []
            ismodtempClear = True
        
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

    # Read from files
    path = askopenfilename()
    if path != '':
        print("user chose", path)
        imgPathEntry.insert(0, path)
        processImg(path)
    else:
        print("Image Not Selected")
''' End of Opencv processing '''

def saveBtn():
    global resultInsertData
    global modtemp
    coordinates = work.setcoordinates(resultInsertData)
    if int(rTPvalue.get()) != 0 and int(rTPvalue.get()) != 1 and int(rTPvalue.get()) != 2:
        messagebox.showwarning(title="Wrong Reg Type", message="예외구역유형은 0, 1, 2중 하나입니다.")
        raise ValueError("INSERT INTO config_values: FAILURE")
    else:
        insert_data(sIDvalue.get(), dIDvalue.get(), rTPvalue.get(), coordinates, imgPathEntry.get())
        messagebox.showinfo(title="Save Data Success", message="INSERT INTO config_values: SUCCESS")
        # 좌표값, 파일 경로가 값이 있는 상태면 초기화
        if isEmpty(coord_list) != True:
            coord_list.clear()
            temp.clear()
            modtemp.clear()
        if isEmpty(imgPathEntry) != True:
            imgPathEntry.delete(0, END)
            imgPathEntry.insert(0, "")

def deleteBtn():
    delete_data(sIDvalue.get(), dIDvalue.get(), rTPvalue.get())

modify_row_data = None
def updateBtn():
    global modtemp
    global resultModifyData
    if uIDvalue.get() != 'coordinates':
        if int(rTPvalue.get()) != 0 and int(rTPvalue.get()) != 1 and int(rTPvalue.get()) != 2:
            messagebox.showwarning(title="Wrong Reg Type", message="예외구역유형은 0, 1, 2중 하나입니다.")
            raise ValueError("INSERT INTO config_values: FAILURE")
        else:
            if uIDvalue.get() != 'site_id' or uIDvalue.get() != 'device_id':
                messagebox.showwarning(title="Wrong Column Name", message="해당 항목이 없습니다.")
            else:
                update_data(uIDvalue.get(), uVLvalue.get(), sIDvalue.get(), dIDvalue.get(), rTPvalue.get())

    elif uIDvalue.get() == 'coordinates':
        modify_row_data, mod_imgPath = select_row(sIDvalue.get(), dIDvalue.get(), rTPvalue.get())

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
        coordinates = work.setcoordinates(resultModifyData)
        uVLEntry.insert(0, coordinates)
        update_data(uIDvalue.get(), uVLvalue.get(), sIDvalue.get(), dIDvalue.get(), rTPvalue.get())
    
if __name__ == "__main__":
    baserow = 0

    ''' Image Load Part '''
    imgPathEntry = Entry(win, width=15)
    imgPathEntry.grid(row=baserow+1, column=1)
    Button(text="이미지 불러오기", command=openDrawImg).grid(row=baserow+1, column=0, padx=10, pady=10)
    ''' Image Load Part End '''

    ''' Save Part '''
    site_id = Label(win, text="Site ID", font=('Arial', 10))
    device_id = Label(win, text="Device ID", font=('Arial', 10))
    reg_type = Label(win, text="Reg Type", font=('Arial', 10))
    site_id.grid(row=baserow+3)
    device_id.grid(row=baserow+4)
    reg_type.grid(row=baserow+5)

    sIDvalue = StringVar(win, value="사이트ID")
    dIDvalue = StringVar(win, value="기기ID")
    rTPvalue = StringVar(win, value="예외구역유형")

    sIDEntry = Entry(win, width=15, textvariable = sIDvalue)
    dIDEntry = Entry(win, width=15, textvariable = dIDvalue)
    rTPEntry = Entry(win, width=15, textvariable = rTPvalue)

    sIDEntry.grid(row=baserow+3, column=1)
    dIDEntry.grid(row=baserow+4, column=1)
    rTPEntry.grid(row=baserow+5, column=1)

    Button(text="저장", width=15, command=saveBtn).grid(row=baserow+6, column=1, padx=10, pady=10)
    ''' Save Part End'''

    ''' Delete Part '''
    Button(text="삭제", width=15, command=deleteBtn).grid(row=baserow+7, column=1)
    ''' Delete Part End '''
    
    ''' Modify Part '''
    uIDvalue = StringVar(win, value="항목 이름")
    uVLvalue = StringVar(win, value="항목 값")

    uIDEntry = Entry(win, width=15, textvariable = uIDvalue)
    uVLEntry = Entry(win, width=15, textvariable = uVLvalue)

    uIDEntry.grid(row=baserow+4, column=3)
    uVLEntry.grid(row=baserow+5, column=3)
    Button(text="수정", width=15, command=updateBtn).grid(row=baserow+6, column=3)
    ''' Modify Part End '''

    win.mainloop()
