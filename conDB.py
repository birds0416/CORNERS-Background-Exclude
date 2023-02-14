import psycopg2
from psycopg2.extensions import AsIs
from config import config

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
def insert_data(site_id, device_id, reg_type, coordinates):
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
        print("INSERT INTO config_values: SUCCESS")

        # close communication with the database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print("INSERT INTO config_values: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

# DB 테이블에서 데이터 삭제
def delete_data(item_id, item_val):
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
        cur.execute("DELETE FROM config_values WHERE %s = %s", [AsIs(item_id), item_val])

        # get the number of updated rows
        rows_deleted = cur.rowcount

        # Commit the changes to the database
        conn.commit()
        print("DELETE FROM config_values: SUCCESS")

        # Close communication with the PostgreSQL database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print("DELETE FROM config_values: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return rows_deleted

# DB 테이블에서 데이터 업데이트
def update_data(update_item, update_val, item_id, item_val):
    """ update vendor name based on the vendor id """
    sql = """ UPDATE config_values
                SET %s = %s
                WHERE %s = %s"""
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
        cur.execute(sql, [AsIs(update_item), update_val, AsIs(item_id), item_val])

        # get the number of updated rows
        updated_rows = cur.rowcount

        # Commit the changes to the database
        conn.commit()
        print("UPDATE config_values: SUCCESS")

        # Close communication with the PostgreSQL database
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print("UPDATE config_values: FAILURE")
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return updated_rows