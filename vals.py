class SpacePos:

    def __init__(self):
        self.reg_type = None
        self.site_id = None
        self.device_id = None
        self.coordinates = ""

        self.triangle = True

    def settriangle(self, val):
        self.triangle = val
        return self.triangle

    def setcoordinates(self, coor_list, triangle):
        # 좌표 순서는 RT, LT, LB, RB 순서로 들어옴
        # TODO
        # 사각형이 아닌 삼각형일 경우 처리 필요
        res = ""
        cnt = 0

        if triangle:
            for item in coor_list:
                cnt += 1
                if cnt > 3:
                    res += " : "
                    cnt = 1
                res += str(item[0]) + "," + str(item[1]) + ", "
                if cnt == 3:
                    res = res[:len(res) - 2]
        else:
            for item in coor_list:
                cnt += 1
                if cnt > 4:
                    res += " : "
                    cnt = 1
                res += str(item[0]) + "," + str(item[1]) + ", "
                if cnt == 4:
                    res = res[:len(res) - 2]

        return res

    
    



