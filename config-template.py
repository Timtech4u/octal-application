from os import path

META_TOP_LEVEL = path.realpath('..')

# logging directory for production
LOG_PATH = path.realpath('..')

# change this path to specify a different local database directory
TOP_DB_PATH = path.join(META_TOP_LEVEL, 'local_dbs')

DJANGO_DB_FILE = path.join(TOP_DB_PATH, 'django_db', 'db.sqlite')

# settings when running django development server
SERVER_IP   = '0.0.0.0'  # set to 0.0.0.0 to access externally
SERVER_PORT = 8080

# Content/App-server Debug level
DEBUG = True

#  hack to obtain ports in bash script
if __name__ == "__main__":
    print SERVER_IP
    print SERVER_PORT
