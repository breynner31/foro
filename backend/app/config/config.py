import os

config= {

    'app': {
        'host': os.getenv('HOST', '0.0.0.0'),
        'port': os.getenv('PORT', 5009),
        'debug': os.getenv('DEGUB', False),
    },
    'database':{
        'host': os.getenv('DB_HOST', 'db'),
        'port': os.getenv('PORT', 3306),
        'user': os.getenv('USER', 'root'),
        'password': os.getenv('PASSWORD', '4zm6hj7U1/97P=£'),
        'database': os.getenv('DATABASE', 'db_foro')
    }
}