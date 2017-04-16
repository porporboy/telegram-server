import pymysql.cursors
import json
import atexit


config = json.load(open('creds/db.json'))

connection = pymysql.connect(host=config.get('host'),
                             user=config.get('user'),
                             password=config.get('pass'),
                             port=config.get('port'),
                             db=config.get('db'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def cleanup():
    if connection:
        connection.close()
        print('Closed connection to db')

def read(sql, params=None):
    """
    DB read operations. fetchone() will be used if 'LIMIT 1' is present in the query. 
    Otherwise, fetchall() will be used.
    @param {str} sql: SQL querystring
    @param {tuple} params: to be formatted into the SQL querystring
    @return result: {list} and {dict} for fetchall() and fetchone() respectively.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            if 'LIMIT 1' in sql.upper():
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()

            print('DB: executed {} ---- result: {}'.format(sql, result))
            return result
    except Exception as err:
        print('DB err: %r' % err)


def write(sql, params=None):
    """
    DB write operations.
    @param {str} sql: SQL querystring
    @param {tuple} params: to be formatted into the SQL querystring
    @return result: {list} and {dict} for fetchall() and fetchone() respectively.
    """
    try:
        with connection.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, params)

            print('DB: executed {}'.format(sql))

        connection.commit()

    except Exception as err:
        print('DB err: %r' % err)

def insert_one(table_name, column_pairs):
    """
    Basic helper function to insert a new row into db.
    @param {str} table_name: name of table to insert into. WARNING: unsafe operation: should not
            be arbitrary input.
    @param {dict} column_pairs: a key-value pair representing the columns and their
            corresponding values in a row. WARNING: keys should not be arbitrary input, only values.
    """
    sql = (
        """
        INSERT INTO {table_name} ({columns}) VALUES (%(values)s)
        """.format(**{
            'table_name': table_name,
            'columns': '{}'.format(','.join([str(key) for key in column_pairs.keys()])),
        })
        )

    params = {
        'values': ','.join([str(val) for val in column_pairs.values()]),
    }
    write(sql, params)