from psycopg2.pool import ThreadedConnectionPool
import psycopg2
import threading
import uuid
import time

bouncer_name = 'testdb'
database_name = 'salary'
port = 5432

pool = ThreadedConnectionPool(5, 50, database= database_name, port=port)
n= 0

def test_func(use_pool=False):
    global n
    while n<30000:
        try:
            if use_pool:
                conn = pool.getconn()
            else:
                conn = psycopg2.connect(database=database_name, port=port)
        except Exception as e:
            continue
        cr = conn.cursor()
        cr.execute('select * from market_salary_data where id = 100')
        data = cr.fetchall()
        if use_pool:
            pool.putconn(conn)
        else:
            conn.close()

        if n%30 == 0:
            print(n)
        n+=1
        



test_pool = []

for a in range(0, 50):
    test_pool.append(threading.Thread(target=test_func))
start_time = time.time()
print('start')
for a in test_pool:
    a.start()

for a in test_pool:
    a.join()
print('end: use {} second'.format(time.time() - start_time))
