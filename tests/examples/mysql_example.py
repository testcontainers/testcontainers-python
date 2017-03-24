from testcontainers import MySqlContainer


def example_with_mysql():
    mysql = MySqlContainer().start()
    mysql.stop()


example_with_mysql()
