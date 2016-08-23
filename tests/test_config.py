from testcontainers import mysql

config = mysql.MySqlConfig()

config.username = "root"

print config.username
