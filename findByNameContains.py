import sys
import logging
import pymysql
import json
import os
from decimal import *

# rds settings
user_name = os.environ["USER_NAME"]
password = os.environ["PASSWORD"]
rds_host = os.environ["RDS_HOST"]
db_name = os.environ["DB_NAME"]
# rds_port = int(os.environ["RDS_PORT"])

rds_port = int(os.getenv('RDS_PORT', 3306))
  

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# create the database connection outside of the handler to allow connections to be
# re-used by subsequent function invocations.
try:
    conn = pymysql.connect(
        port=rds_port,
        host=rds_host,
        user=user_name,
        passwd=password,
        db=db_name,
        connect_timeout=5,
    )

except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")


def lambda_handler(message, context):
    """
    This gets records by name
    """
    # message = event['Records'][0]['body']

    # data = json.dumps(message)
    # data = message
    # logger.info(data)
    body = json.loads(message["body"])
    # logger.info(body)
    # logger.info(type(body))

    name = body["name"]

    logger.info(name)

    item_count = 0

    with conn.cursor() as cursor:

        namewild = "%" + name + "%"        
        cursor.execute("SELECT name, price FROM catalog WHERE name like %s", (namewild,))
              
        # print(cursor._executed)

        row_headers=[x[0] for x in cursor.description] #this will extract row headers
        rv = cursor.fetchall()

        json_data = []
        for row in rv:
            row_data = []
            for data in row:
                # print(type(data))
                if type(data) is Decimal:
                    # row_data.append(float(Decimal(data).quantize(Decimal('.01'))))
                    row_data.append("%.2f" % float(Decimal(data).quantize(Decimal('.01'))))
                else:
                    row_data.append(str(data))
            json_data.append(dict(zip(row_headers,row_data)))
        output_json = (json.dumps(json_data))  

    response = {
        "statusCode": 200,
        "headers": {},
        "body": output_json
    }

    return response
