from testcontainers import mysql

config = mysql.ContainerConfig()
print config.user
print config.passwd
