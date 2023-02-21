def setcoordinates(coor_list):
    # 좌표 순서는 RT, LT, LB, RB 순서로 들어옴
    # TODO
    # 사각형이 아닌 삼각형일 경우 처리 필요
    res = ""
    cnt = 0

    for shape in coor_list:
        for pnt in shape[:len(shape) - 1]:
            res += str(pnt[0]) + "," + str(pnt[1]) + ", "
        res += str(shape[len(shape) - 1][0]) + "," + str(shape[len(shape) - 1][1]) + " : "
    
    res = res[:len(res) - 3]

    return res

    
    



