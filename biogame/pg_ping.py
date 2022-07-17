import psycopg2, sys
from os import environ

try:
	connection = psycopg2.connect(
	    database=environ.get('POSTGRES_DB'),
	    user=environ.get('POSTGRES_USER'),
	    password=environ.get('POSTGRES_PASSWORD'),
	    host=environ.get('POST_HOST'),
	    port=environ.get('POST_PORT')
	)
except psycopg2.OperationalError as e:
	sys.exit("The database is not ready. Waiting for 5 seconds")