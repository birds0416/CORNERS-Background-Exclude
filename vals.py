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

    # def setsite_id(self, id):
    #     self.site_id = id
    #     return self.site_id
    
    # def setdev_id(self, id):
    #     self.device_id = id
    #     return self.device_id
    
    # def setreg_type(self): # num은 0 / 1 / 2 중에 하나여야 한다
    #     # num = 0 -> 지게차 In/Out 구역
    #     # num = 1 -> 전체객체 예외 구역
    #     # num = 2 -> 지게차 예외구역
    #     while True:
    #         num = int(input("예외구역 유형을 설정하세요: "))
    #         if num == 0 or num == 1 or num == 2:
    #             break
    #         print("예외구역유형 값은 0 / 1 / 2 중에 하나여야합니다.")

    #     self.reg_type = num
    #     return self.reg_type

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

    
    



