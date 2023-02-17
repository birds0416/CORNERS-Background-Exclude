import json
import psycopg2
from psycopg2.extensions import AsIs
from tkinter import messagebox

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
            if obj["site_id"] == site_id and obj["device_id"] == device_id and obj["reg_type"] == reg_type:
                del temp[idx]
                print("DELETE FROM data.json: SUCCESS")
            else:
                print("DELETE FROM data.json: NO MATCHING DATA")
                break

    with open("data.json", 'w') as f:
        json.dump(file_data, f, indent=4)

def update_in_json(site_id, device_id, reg_type, update_id, update_data, filename='data.json'):
    with open(filename, 'r', encoding='utf-8') as file:
        file_data = json.load(file)

        temp = file_data.get("DB_Data")
        for idx, obj in enumerate(temp):
            if obj["site_id"] == site_id and obj["device_id"] == device_id and obj["reg_type"] == reg_type:
                origin = temp[idx][update_id]
                temp[idx][update_id] = update_data
                print("UPDATE data.json: SUCCESS")
            else:
                print("UPDATE data.json: NO MATCHING DATA")
                break

    with open("data.json", 'w') as f:
        json.dump(file_data, f, indent=4)

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
            print('Database connection closed.')

# DB에 연결됐는지 확인
def isCon():
    return connection

# DB에 테이블 생성
def create_table():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS config_values (
            site_id INT NOT NULL,
            device_id INT NOT NULL,
            reg_type INT NOT NULL,
            coordinates TEXT
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
    sql = """INSERT INTO config_values(site_id, device_id, reg_type, coordinates) VALUES(%s, %s, %s, %s)"""
    record_data = (site_id, device_id, reg_type, coordinates)
    conn = None

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
        add_data = {
            "site_id": site_id,
            "device_id": device_id,
            "reg_type": reg_type,
            "coordinates": coordinates,
            "img_path": imgPath
        }
        add_to_json(add_data)
        print("INSERT INTO config_values: SUCCESS")

        # close communication with the database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        add_data = {
            "site_id": site_id,
            "device_id": device_id,
            "reg_type": reg_type,
            "coordinates": coordinates,
            "img_path": imgPath
        }
        add_to_json(add_data)
        print("INSERT INTO config_values: FAILURE")
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
        cur.execute("DELETE FROM config_values WHERE site_id = %s and device_id = %s and reg_type = %s", (site_id, device_id, reg_type))

        # get the number of updated rows
        rows_deleted = cur.rowcount

        # Commit the changes to the database
        conn.commit()
        if rows_deleted != 0:
            print("DELETE FROM config_values: SUCCESS")
            messagebox.showinfo(title="Delete Data Success", message="DELETE FROM config_values: SUCCESS")
        else:
            print("DELETE FROM config_values: NO MATCHING DATA")
            messagebox.showwarning(title="Delete Data Success", message="DELETE FROM config_values: NO MATCHING DATA")

        delete_from_json(site_id, device_id, reg_type)

        # Close communication with the PostgreSQL database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        delete_from_json(site_id, device_id, reg_type)
        print("DELETE FROM config_values: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return rows_deleted

# DB 테이블에서 데이터 업데이트
def update_data(update_item, update_val, siteID, deviceID, regType):
    """ update vendor name based on the vendor id """
    sql = """ UPDATE config_values
                SET %s = %s
                WHERE site_id = %s and device_id = %s and reg_type = %s"""
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
        cur.execute(sql, [AsIs(update_item), update_val, siteID, deviceID, regType])

        # get the number of updated rows
        updated_rows = cur.rowcount

        # Commit the changes to the database
        conn.commit()
        if updated_rows != 0:
            print("UPDATE config_values: SUCCESS")
            messagebox.showinfo(title="UPDATE config_values Success", message="UPDATE config_values: SUCCESS")
        else:
            print("UPDATE config_values: NO MATCHING DATA")
            messagebox.showwarning(title="UPDATE config_values Success", message="UPDATE config_values: NO MATCHING DATA")

        update_in_json(siteID, deviceID, regType, update_item, update_val)

        # Close communication with the PostgreSQL database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        update_in_json(siteID, deviceID, regType, update_item, update_val)
        print("UPDATE config_values: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return updated_rows

# DB에서 특정 행 데이터 가져오기
def select_row(siteID, deviceID, regType):
    """ select row based on item_id """
    sql = """ select *
                FROM config_values
                WHERE site_id = %s and device_id = %s and reg_type = %s"""
    conn = None
    row = ""
    
    path = ""
    with open('data.json', 'r', encoding='utf-8') as readfile:
        file_data = json.load(readfile)
        temp = file_data.get("DB_Data")
        for idx, obj in enumerate(temp):
            if obj["site_id"] == siteID and obj["device_id"] == deviceID and obj["reg_type"] == regType:
                path = obj["img_path"]
                break

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
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return row, path