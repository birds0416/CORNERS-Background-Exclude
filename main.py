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
from conDB import connect, isCon, create_table, insert_data, delete_data, update_data, select_row

# Import Tkinter
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox

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
win.geometry("400x800")

# returns is value is None or not
def isEmpty(value):
    return value == None

''' From here is image processing by opencv'''
coord_list = []
temp = []
def processImg(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, (540, 960))
    
    def click_event(event, x, y, flags, param):
        # checking for left mouse clicks
        # 클릭하여 좌표지정
        global coord_list
        global temp
        if event == cv2.EVENT_LBUTTONDOWN:
            # displaying the coordinates on the Shell
            coord_list.append([x * 2, y * 2])
            temp.append([x, y])
            
        if event == cv2.EVENT_RBUTTONDOWN:
            if coord_list != None:
                coord_list = coord_list[:len(coord_list) - 1]
                temp = temp[:len(temp) - 1]
        
    # Display the image
    cv2.imshow("image", img)
    cv2.setMouseCallback('image', click_event)

    # Wait until the user closes the window
    while True:
        cv2.imshow("image", img)

        if temp != None:
            img_copy = img.copy()
            for i in range(len(temp)):
                cv2.circle(img_copy, temp[i], 1, (255, 255, 0), 5)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 2:
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 3:
            work.settriangle(True)
            # Draw the triangle on the image
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) >= 4 and len(coord_list) < 6:
            work.settriangle(False)
            # Draw the triangle on the image
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp[:4]]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 6:
            work.settriangle(True)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp[:3]]), True, (0, 255, 0), 2)
            cv2.polylines(img_copy, np.int32([temp[3:]]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)
        
        if len(coord_list) == 7:
            work.settriangle(True)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp[:4]]), True, (0, 255, 0), 2)
            cv2.polylines(img_copy, np.int32([temp[4:]]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 8:
            work.settriangle(False)
            # Draw the triangle on the image
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp[:4]]), True, (0, 255, 0), 2)
            cv2.polylines(img_copy, np.int32([temp[4:]]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cv2.destroyWindow("image")
            break

modtemp = []
def modifyImg(image_path, pnt_datas):
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, (540, 960))
    imgPathEntry.insert(0, image_path)
    uVLEntry.delete(0, END)

    global modtemp
    global coord_list
    if isEmpty(coord_list) != True:
        coord_list.clear()

    for pnt in pnt_datas:
        modtemp.append([pnt[0] / 2, pnt[1] / 2])

    ''' cv2.EVENT_MOUSEMOVE 마우스 포인터가 박스 위에 있을 때 위한 그림 좌표 계산 '''
    # xlist = []
    # ylist = []
    # for p in modtemp:
    #     xlist.append(p[0])
    #     ylist.append(p[1])

    # xmin = min(xlist)
    # xmax = max(xlist)
    # ymin = min(ylist)
    # ymax = max(ylist)

    global ismodtempClear
    ismodtempClear = False

    def click_event(event, x, y, flags, param):
        # checking for shift input
        # shift키 누르면 지정좌표 색바꿈
        global coord_list
        global line_color
        global modtemp
        global ismodtempClear
        if flags & cv2.EVENT_FLAG_SHIFTKEY:
            line_color = (0, 0, 255)
            if event == cv2.EVENT_RBUTTONDOWN:
                modtemp.clear()
                ismodtempClear = True
        else:
            line_color = (0, 255, 0)

        if len(modtemp) != 0:
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([modtemp]), True, line_color, 2)
            cv2.imshow("image", img_copy)
        
        if ismodtempClear:
            if event == cv2.EVENT_LBUTTONDOWN:
                coord_list.append([x * 2, y * 2])
                modtemp.append([x, y])
                cv2.circle(img, (x, y), 3, (255, 255, 0), 5)


    # Display the image
    cv2.imshow("image", img)
    cv2.setMouseCallback('image', click_event)
    global line_color
    line_color = (0, 255, 0)
    
    while True:
        cv2.imshow("image", img)

        if len(coord_list) == 2 or len(pnt_datas) == 2:
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([modtemp]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 3 or len(pnt_datas) == 3:
            work.settriangle(True)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([modtemp]), True, line_color, 2)
            cv2.imshow("image", img_copy)
        
        if len(coord_list) >= 4 and len(coord_list) < 6 or len(pnt_datas) == 4:
            work.settriangle(False)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([modtemp[:4]]), True, line_color, 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 6 or len(pnt_datas) == 6:
            work.settriangle(True)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([modtemp[:3]]), True, line_color, 2)
            cv2.polylines(img_copy, np.int32([modtemp[3:]]), True, line_color, 2)
            cv2.imshow("image", img_copy)
        
        if len(coord_list) == 7:
            work.settriangle(False)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([modtemp[:4]]), True, line_color, 2)
            cv2.polylines(img_copy, np.int32([modtemp[4:]]), True, line_color, 2)
            cv2.imshow("image", img_copy)
        
        if len(coord_list) == 8 or len(pnt_datas) == 8:
            work.settriangle(False)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([modtemp[:4]]), True, line_color, 2)
            cv2.polylines(img_copy, np.int32([modtemp[4:]]), True, line_color, 2)
            cv2.imshow("image", img_copy)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            cv2.destroyAllWindows()
            break
            
def openDrawImg():
    global coord_list
    global temp

    # Read from files
    path = askopenfilename()
    print("user chose", path)
    imgPathEntry.insert(0, path)
    processImg(path)
''' End of Opencv processing '''

def saveBtn():
    global coord_list
    global temp
    global modtemp
    coordinates = work.setcoordinates(coord_list, work.triangle)
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
    global coord_list
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
        tempdata = modify_row_data[3]
        pnts = []
        if ':' in tempdata:
            tempdata = modify_row_data[3].split(":")
        else:
            tempdata = modify_row_data[3].split(", ")
        
        for tmp in tempdata:
            X = int(tmp.split(',')[0])
            Y = int(tmp.split(',')[1])
            pnts.append([X, Y])

        modifyImg(mod_imgPath, pnts)
        coordinates = work.setcoordinates(coord_list, work.triangle)
        uVLEntry.insert(0, coordinates)
        update_data(uIDvalue.get(), uVLvalue.get(), sIDvalue.get(), dIDvalue.get(), rTPvalue.get())

def sample():
    print("cbal")
    
if __name__ == "__main__":
    baserow = 0
    empty0 = Label(win, text='     \n   ')
    empty0.grid(column=0, row=baserow)
    Button(text="박스 그리기", command=sample).grid(row=0, column=0)
    Button(text="박스 저장", command=sample).grid(row=0, column=1)

    ''' Image Load Part '''
    imgPathEntry = Entry(win, width=15)
    imgPathEntry.grid(row=baserow+1, column=1)
    Button(text="이미지 불러오기", command=openDrawImg).grid(row=baserow+1, column=0)
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

    Button(text="DB저장", command=saveBtn).grid(row=baserow+6, column=1)
    ''' Save Part End'''

    ''' Delete Part '''
    Button(text="DB삭제", command=deleteBtn).grid(row=baserow+6, column=2, padx=10)
    ''' Delete Part End '''
    
    ''' Modify Part '''
    uIDvalue = StringVar(win, value="항목 이름")
    uVLvalue = StringVar(win, value="항목 값")

    uIDEntry = Entry(win, width=10, textvariable = uIDvalue)
    uVLEntry = Entry(win, width=10, textvariable = uVLvalue)

    uIDEntry.grid(row=baserow+4, column=3)
    uVLEntry.grid(row=baserow+5, column=3)
    Button(text="DB수정", command=updateBtn).grid(row=baserow+6, column=3)
    ''' Modify Part End '''

    win.mainloop()