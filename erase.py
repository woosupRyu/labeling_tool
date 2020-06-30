# -*- coding: utf-8 -*-
from DCD_DB_API_master.db_api import DB


def reset_table(db):
    db.drop_table(table='Bbox')
    db.drop_table(table='Mask')
    db.drop_table(table='Object')
    db.drop_table(table='Image')
    db.drop_table(table='Location')
    db.drop_table(table='Category')
    db.drop_table(table='Environment')
    db.drop_table(table='Grid')
    db.drop_table(table='SuperCategory')

if __name__ == "__main__":

    # cunnect to MYSQL Server
    mydb = DB(ip='192.168.10.69',
              port=3306,
              user='root',
              password='return123',
              db_name='test')

    # reset tables
    reset_table(mydb)

    # table 초기화
    mydb.init_table()
