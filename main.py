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

import vals
import cv2
import numpy as np
from conDB import connect, isCon, create_table, insert_data, delete_data, update_data

# Import Tkinter
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename

connect()
if isCon() == False:
    # TODO
    '''
    데이터 베이스 연동이 안되는 경우 파일로 설정 저장
    '''
    print("Connection to Database FAILURE")
    print("Processing alternate solution...")
    with open('result.txt', 'w') as file:
            file.write(" site_id | device_id | reg_type |          coordinates           \n")
            file.write("---------+-----------+----------+--------------------------------\n")

work = vals.SpacePos()
create_table()

#Create an instance of Tkinter frame
win= Tk()
win.title("대상LS 예외구역 설정 Tool")
#Set the geometry of Tkinter frame
win.geometry("400x600")

# win.withdraw() # prevents an empty tkinter window from appearing
''' From here is image processing by opencv'''
coord_list = []
temp = []
def processImg():
    # Read from files
    path = askopenfilename()
    print("user chose", path)
    imgPathEntry.insert(0, path)

    # Define a global variable to store the ROI
    roi = None
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    img = cv2.resize(img, (540, 960))

    def click_event(event, x, y, flags, param):
        # checking for left mouse clicks
        if event == cv2.EVENT_LBUTTONDOWN:
            # displaying the coordinates on the Shell
            print(x, ' ', y)
            coord_list.append([x * 2, y * 2])
            temp.append([x, y])
    
            # displaying the coordinates on the image window
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, str(x) + ',' + str(y), (x,y), font, 1, (255, 255, 0), 2)
            cv2.imshow('image', img)

    # Display the image
    cv2.imshow("image", img)
    cv2.setMouseCallback('image', click_event)

    # Wait until the user closes the window
    while True:
        cv2.imshow("image", img)

        if len(coord_list) == 3:
            work.settriangle(True)
            # Draw the triangle on the image
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 4:
            work.settriangle(False)
            # Draw the triangle on the image
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp]), True, (0, 255, 0), 2)
            cv2.imshow("image", img_copy)

        if len(coord_list) == 6:
            work.settriangle(False)
            img_copy = img.copy()
            cv2.polylines(img_copy, np.int32([temp[:3]]), True, (0, 255, 0), 2)
            cv2.polylines(img_copy, np.int32([temp[3:]]), True, (0, 255, 0), 2)
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
''' End of Opencv processing '''

def saveBtn():
    coordinates = work.setcoordinates(coord_list, work.triangle)
    if isCon():
        insert_data(sIDvalue.get(), dIDvalue.get(), rTPvalue.get(), coordinates)
    else:
        with open('result.txt', 'a') as file:
            val = ""
            cnt = 0
            for pnt in coord_list:
                cnt += 1
                if cnt > 4:
                    val += " : "
                    cnt = 0
                val += str(pnt[0]) + "," + str(pnt[1]) + ", "
            file.write("  "+  str(site_id) + " |        " + str(device_id) + " |        " + str(reg_type) + " | " + val)
            file.close()

def deleteBtn():
    delete_data(wID.get(), wVL.get())

def updateBtn():
    print("Sibal")

# def updateBtn():
#     update_data(update_set_id, update_set_val, update_where_id, update_where_val)

baserow = 0
empty0 = Label(win, text='     \n   ')
empty0.grid(column=0, row=baserow)

''' Image Load Part '''
imgPathEntry = Entry(win, width=20)
imgPathEntry.grid(row=baserow+1, column=1)
Button(text="이미지 불러오기", command=processImg).grid(row=baserow+1, column=0)
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

sIDEntry = Entry(win, textvariable = sIDvalue)
dIDEntry = Entry(win, textvariable = dIDvalue)
rTPEntry = Entry(win, textvariable = rTPvalue)

sIDEntry.grid(row=baserow+3, column=1)
dIDEntry.grid(row=baserow+4, column=1)
rTPEntry.grid(row=baserow+5, column=1)

Button(text="DB저장", command=saveBtn).grid(row=baserow+6, column=1)
Button(text="DB수정", command=updateBtn).grid(row=baserow+6, column=2)
''' Save Part End'''

empty2 = Label(win, text='     \n   ')
empty2.grid(column=0, row=baserow+7)

''' Delete Part '''
where_id = Label(win, text="Where ID", font=('Arial', 10))
where_val = Label(win, text="Where Value", font=('Arial', 10))

where_id.grid(row=baserow+8)
where_val.grid(row=baserow+9)

wID = StringVar(win, value="항목이름")
wVL = StringVar(win, value="항목 값")

wIDEntry = Entry(win, textvariable = wID)
wVLEntry = Entry(win, textvariable = wVL)

wIDEntry.grid(row=baserow+8, column=1)
wVLEntry.grid(row=baserow+9, column=1)

Button(text="DB삭제", command=deleteBtn).grid(row=baserow+10, column=1)
''' Delete Part End '''

empty3 = Label(win, text='     \n   ')
empty3.grid(column=0, row=baserow+11)

''' Update Part '''
# update_set_id = Label(win, text="Set ID", font=('Arial', 10))
# update_set_val = Label(win, text="Set Value", font=('Arial', 10))
# update_where_id = Label(win, text="Where ID", font=('Arial', 10))
# update_where_val = Label(win, text="Where Value", font=('Arial', 10))

# update_set_id.grid(row=baserow+11)
# update_set_val.grid(row=baserow+12)
# update_where_id.grid(row=baserow+13)
# update_where_val.grid(row=baserow+14)

# uSID = StringVar()
# uSVL = StringVar()
# uWID = StringVar()
# uWVL = StringVar()

# uSIDEntry = Entry(win, textvariable = uSID)
# uSVLEntry = Entry(win, textvariable = uSVL)
# uWIDEntry = Entry(win, textvariable = uWID)
# uWVLEntry = Entry(win, textvariable = uWVL)

# uSIDEntry.grid(row=baserow+11, column=1)
# uSVLEntry.grid(row=baserow+12, column=1)
# uWIDEntry.grid(row=baserow+13, column=1)
# uWVLEntry.grid(row=baserow+14, column=1)

# Button(text="DB업데이트", command=getvals).grid(row=baserow+15, column=1)
''' Update Part End '''

win.mainloop()