# -*- coding:utf-8 -*-

import sys
import os
import time
import mysql.connector
from mysql.connector import Error

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance as Board

board = Board()

def connect_to_database():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="raspberry",
            database="sensordaten"
        )
    except Error as err:
        print(f"Error: {err}")
        sys.exit(1)

def print_distance(dis):
    if board.last_operate_status == board.STA_OK:
        print("Distance %d mm" % dis)
    elif board.last_operate_status == board.STA_ERR_CHECKSUM:
        print("ERROR")
    elif board.last_operate_status == board.STA_ERR_SERIAL:
        print("Serial open failed!")
    elif board.last_operate_status == board.STA_ERR_CHECK_OUT_LIMIT:
        print("Above the upper limit: %d" % dis)
    elif board.last_operate_status == board.STA_ERR_CHECK_LOW_LIMIT:
        print("Below the lower limit: %d" % dis)
    elif board.last_operate_status == board.STA_ERR_DATA:
        print("No data!")

if __name__ == "__main__":
    mydb = connect_to_database()
    cursor = mydb.cursor()
    
    dis_min = 0 
    dis_max = 4500 
    board.set_dis_range(dis_min, dis_max)
    
    try:
        while True:
            distance = board.getDistance()
            print_distance(distance)

            if distance > 0 and distance < dis_max:
                now = time.strftime('%Y-%m-%d %H:%M:%S')

                sql = "INSERT INTO Dist (dist, timestamp) VALUES (%s, %s)"
                val = (distance, now)

                try:
                    cursor.execute(sql, val)
                    mydb.commit()
                    print(cursor.rowcount, "record inserted.")
                except Error as err:
                    print(f"Failed to insert record into MySQL table: {err}")

            else:
                print("Ungültiger Wert, wird nicht gespeichert.")

            time.sleep(600)
    except KeyboardInterrupt:
        print("Programm beendet")
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()
