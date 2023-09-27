import keyring
import mysql.connector
from py_code.classes.site_info import create_site_info_table_statement


class MysqlConnection:
    def __init__(self, config):
        self.user = keyring.get_password("mysql", "username")
        self.password = keyring.get_password("mysql", "password")
        self.host = config['host']
        self.database = config['database']

        # check if the target database exists; if not, create it
        try:
            self.conn = self.get_connection()
        except mysql.connector.DatabaseError:
            self.set_up_database()
            self.conn = self.get_connection()

    def __del__(self):
        self.close_connection()

    def set_up_database(self):
        db_conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password
        )
        cursor = db_conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {0};".format(self.database))
        cursor.close()

    def set_up_tables(self):
        self.execute_sql_statement(create_site_info_table_statement)

    def get_connection(self):
        return mysql.connector.connect(host=self.host, user=self.user, password=self.password, database=self.database)

    def close_connection(self):
        self.conn.close()

    def execute_sql_query(self, query, values=None):
        cursor = self.conn.cursor()
        if values is not None:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        if result is not None and len(result) == 0:
            return None
        return result

    def execute_sql_statement(self, statement, values=None):
        cursor = self.conn.cursor()
        if values is not None:
            cursor.execute(statement, values)
        else:
            cursor.execute(statement)
        self.conn.commit()
        cursor.close()
