import json
import psycopg2

from psycopg2.extensions import AsIs
from tkinter import messagebox
from datetime import datetime, date

from config import config

# Json handling
def add_to_json(new_data, filename='data.json'):
    with open(filename, 'r+') as file:
        file_data = json.load(file)
        file_data["DB_Data"].append(new_data)
        print("INSERT INTO data.json: SUCCESS")
        file.seek(0)
        json.dump(file_data, file, indent=4)

def delete_from_json(site_id, device_id, reg_type, filename='data.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        file_data = json.load(file)

        temp = file_data.get("DB_Data")
        for idx, obj in enumerate(temp):
            if obj["site_id"] == site_id and obj["dev_id"] == device_id and obj["reg_type"] == reg_type:
                del temp[idx]
                print("DELETE FROM data.json: SUCCESS")
            else:
                print("DELETE FROM data.json: NO MATCHING DATA")

    with open("data.json", 'w') as f:
        json.dump(file_data, f, indent=4)

def update_in_json(site_id, device_id, reg_type, update_data, imgPath, filename='data.json'):
    isUpdated = False

    now = datetime.now()
    today = date.today()
    current_time = now.strftime("%H:%M:%S")
    curr_date = str(today) + ' ' + current_time

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            file_data = json.load(file)

            temp = file_data.get("DB_Data")
            for idx, obj in enumerate(temp):
                if obj["site_id"] == site_id and obj["dev_id"] == device_id and obj["reg_type"] == reg_type:
                    temp[idx]["pos"] = update_data
                    if update_data == "":
                        print("UPDATE data.json: Update Data EMPTY")
                        isUpdated = False
                    print("UPDATE data.json: SUCCESS")
                    isUpdated = True
                else:
                    print("UPDATE data.json: NO MATCHING DATA in data.json")
            
            if isUpdated != True:
                print("UPDATE data.json: FAILURE - NO DATA")
                print("UPDATE data.json: ADDING DATA...")

                insert_data = {
                    "site_id": site_id,
                    "dev_id": device_id,
                    "reg_type": reg_type,
                    "pos": update_data,
                    "img_path": imgPath,
                    "saved time": curr_date
                }

        if isUpdated == True:
            with open(filename, 'w') as f:
                json.dump(file_data, f, indent=4)
        else:
            with open(filename, 'r+') as file:
                file_data = json.load(file)
                file_data["DB_Data"].append(insert_data)
                print("INSERT INTO data.json: SUCCESS")
                file.seek(0)
                json.dump(file_data, file, indent=4)
    
    except:
        newJson = {"DB_Data":[]}
        json_obj = json.dumps(newJson, indent=4)
        with open("data.json", "w") as outfile:
            outfile.write(json_obj)

        insert_data = {
            "site_id": site_id,
            "dev_id": device_id,
            "reg_type": reg_type,
            "pos": update_data,
            "img_path": imgPath,
            "saved time": curr_date
        }
        add_to_json(insert_data)

def isJsonEmpty(filename='data.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        temp = file_data.get("DB_Data")
        return temp == []

# DB에 연결
def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    global connection
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	    # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        connection = True
        db_version = cur.fetchone()
        print(db_version)
       
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        connection = False
        print("Connect to PostgreSQL database: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connected.', params)

# DB에 연결됐는지 확인
def isCon():
    return connection

# DB에 테이블 생성
def create_table():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS tbvision_except_region (
            site_id INT NOT NULL,
            dev_id INT NOT NULL,
            reg_type INT NOT NULL,
            pos TEXT
        )
        """)

    conn = None
    try:
        # read the connection parameters
        params = config()

        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # create table one by one
        cur.execute(commands)

        # close communication with the PostgreSQL database server
        cur.close()

        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

# DB 테이블에 데이터 삽입
def insert_data(site_id, device_id, reg_type, coordinates, imgPath):
    """ insert a new vendor into the item data """
    sql = """INSERT INTO tbvision_except_region(site_id, dev_id, reg_type, pos) VALUES(%s, %s, %s, %s)"""
    record_data = (site_id, device_id, reg_type, coordinates)
    conn = None

    now = datetime.now()
    today = date.today()
    current_time = now.strftime("%H:%M:%S")
    curr_date = str(today) + ' ' + current_time

    add_data = {
        "site_id": site_id,
        "dev_id": device_id,
        "reg_type": reg_type,
        "pos": coordinates,
        "img_path": imgPath,
        "saved time": curr_date
    }
    
    try:
        # read database configuration
        params = config()

        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        # create a new cursor
        cur = conn.cursor()

        # execute the INSERT statement
        cur.execute(sql, record_data)

        # commit the changes to the database
        conn.commit()
        add_to_json(add_data)
        print("INSERT INTO tbvision_except_region: SUCCESS")

        # close communication with the database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        add_to_json(add_data)
        print("INSERT INTO tbvision_except_region: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

# DB 테이블에서 데이터 삭제
def delete_data(site_id, device_id, reg_type):
    """ delete part by id_val """
    conn = None
    rows_deleted = 0

    try:
        # read database configuration
        params = config()

        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        # create a new cursor
        cur = conn.cursor()

        # execute the UPDATE  statement
        cur.execute("DELETE FROM tbvision_except_region WHERE site_id = %s and dev_id = %s and reg_type = %s", (site_id, device_id, reg_type))

        # get the number of updated rows
        rows_deleted = cur.rowcount

        # Commit the changes to the database
        conn.commit()
        if rows_deleted != 0:
            print("DELETE FROM tbvision_except_region: SUCCESS")
        else:
            print("DELETE FROM tbvision_except_region: NO MATCHING DATA")
            messagebox.showwarning(title="Delete Data Success", message="DELETE FROM tbvision_except_region: NO MATCHING DATA")

        delete_from_json(site_id, device_id, reg_type)

        # Close communication with the PostgreSQL database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        delete_from_json(site_id, device_id, reg_type)
        print("DELETE FROM tbvision_except_region: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return rows_deleted

# DB 테이블에서 데이터 업데이트
def update_data(update_val, siteID, deviceID, regType, imgPath):
    """ update vendor name based on the vendor id """
    sql = """ UPDATE tbvision_except_region
                SET pos = %s
                WHERE site_id = %s and dev_id = %s and reg_type = %s"""
    conn = None
    updated_rows = 0

    try:
        # read database configuration
        params = config()

        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        # create a new cursor
        cur = conn.cursor()

        # execute the UPDATE  statement
        cur.execute(sql, [update_val, siteID, deviceID, regType])

        # get the number of updated rows
        updated_rows = cur.rowcount

        # Commit the changes to the database
        conn.commit()
        if updated_rows != 0:
            update_in_json(siteID, deviceID, regType, update_val, imgPath)
            print("UPDATE tbvision_except_region: SUCCESS")
            messagebox.showinfo(title="UPDATE tbvision_except_region Success", message="UPDATE tbvision_except_region: SUCCESS")
        else:
            print("UPDATE tbvision_except_region: NO MATCHING DATA")
            messagebox.showwarning(title="UPDATE tbvision_except_region FAILURE", message="UPDATE tbvision_except_region: NO MATCHING DATA")


        # Close communication with the PostgreSQL database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        update_in_json(siteID, deviceID, regType, update_val, imgPath)
        print("UPDATE tbvision_except_region: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return updated_rows

# DB에서 특정 행 데이터 가져오기
def select_row(siteID, deviceID, regType):
    """ select row based on item_id """
    sql = """ select *
                FROM tbvision_except_region
                WHERE site_id = %s and dev_id = %s and reg_type = %s"""
    conn = None
    row = None

    try:
        # read database configuration
        params = config()

        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)

        # create a new cursor
        cur = conn.cursor()

        # execute the UPDATE  statement
        cur.execute(sql, (siteID, deviceID, regType))
        row = cur.fetchone()

        # Close communication with the PostgreSQL database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        row_data = None
        with open('data.json', 'r', encoding='utf-8') as readfile:
            file_data = json.load(readfile)
            temp = file_data.get("DB_Data")
            for idx, obj in enumerate(temp):
                if obj["site_id"] == siteID and obj["dev_id"] == deviceID and obj["reg_type"] == regType:
                    row_data = (obj["site_id"], obj["dev_id"], obj["reg_type"], obj["pos"])
                    break
        row = row_data
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return row