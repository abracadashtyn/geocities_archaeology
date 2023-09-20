from py_code.mysql_connection import MysqlConnection
from py_code.config.config import Config

if __name__ == "__main__":
    config = Config()
    conn = MysqlConnection(config.get_mysql_config())
    conn.set_up_database()
    conn.set_up_tables()
