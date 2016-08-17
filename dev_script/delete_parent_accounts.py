import psycopg2
try:
    connection = psycopg2.connect("dbname='' user='' host='localhost' password=''")
except:
    print('connection error')
cr = connection.cursor()
cr.execute('select distinct parent_id from account_account where parent_id is not null')
parent_ids = cr.fetchall()
parent_ids = [x[0] for x in parent_ids]
print('se eliminan parent_id')
cr.execute('update account_account set parent_id = NULL')
print('se eliminan cuentas padre')
cr.execute('delete from account_account where id in %s' % (tuple(parent_ids), ))
connection.commit()
connection.close()
