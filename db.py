import pymysql.cursors
import sys
import time

connection = None

def connect():
    global last_count
    global connection
    if connection is not None:
        return

    connection = pymysql.connect(host='beer.shpsec.com',
                                 user='kegbot',
                                 password='kegbot',
                                 db='kegbot',
                                 cursorclass=pymysql.cursors.DictCursor)

def do_query(sql):
    connect()
    try:
        with connection.cursor() as cursor:
            # print 'do_query({})'.format(sql)
            n = cursor.execute(sql)
            result = cursor.fetchall()
            connection.commit()
            # print(result)
            return result

    except Exception as e:
        print 'Exception doing query'
        print 'SQL: {}'.format(sql)
        print '  e: {}'.format(e)
        return None
    
def get_tap_info():
    sql = '''
SELECT t.id AS tap, k.served_volume_ml AS served, full_volume_ml AS full, b.name AS name, b.style AS style, b.description AS description, p.image AS pic_url
FROM core_keg AS k, core_kegtap AS t, core_beverage AS b, core_picture AS p
WHERE t.current_keg_id = k.id AND b.id = k.type_id AND p.id = b.picture_id
ORDER BY t.id
'''
    return do_query(sql)

def get_last_drink():
    sql = '''
SELECT * FROM core_drink ORDER BY id DESC LIMIT 1;
'''
    return do_query(sql)
