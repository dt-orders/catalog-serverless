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
    
    #output_json = {"error": "something went wrong"}
    print(message)
    body = json.loads(message["body"])

    function = body["function"]
    #testing
    #function = "insertItem"
    #body = {"id": 14, "name": "thingie", "price": "102"}
    #body = {"name": "mandy", "price": "102"}

    if (function == "findAll"):
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, price FROM catalog")
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            rv = cursor.fetchall()
            
            json_data = []
            for row in rv:
                row_data = []
                for data in row:
                    if type(data) is Decimal:
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
    elif (function == "findById"):
        item_id = body["id"]
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, price FROM catalog WHERE id =%s", (item_id))
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            rv = cursor.fetchall()
            
            output_json = format_db_output(row_headers, rv)
            print (output_json)
            
            response = {
                "statusCode": 200,
                "headers": {},
                "body": output_json
            }
            
            return response
    elif (function == "insertItem"):
        name = body["name"]
        price = body["price"]
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO catalog (name, price) VALUES (%s, %s)", (name, price))
            conn.commit()
            
            #row_headers=[x[0] for x in cursor.description] #this will extract row headers
            rv = cursor.fetchall()
            print(rv)
            
            #output_json = format_db_output(row_headers, rv)
            #print (output_json)

            
            response = {
                "statusCode": 200,
                "headers": {},
                "body": "inserted"
            }
            
            return response
            
           
    elif (function == "updateItemById"):
        item_id = body["id"]
        name = body["name"]
        price = body["price"]
        with conn.cursor() as cursor:
            cursor.execute("UPDATE catalog SET name=%s, price=%s WHERE id=%s", (name, price, item_id))
            conn.commit()
            rv = cursor.fetchall()
            print(rv)
            
        response = {
                "statusCode": 200,
                "headers": {},
                "body": "updated item"
        }
            
        return response
    elif (function == "deleteItemById"):
        item_id = body["id"]
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM catalog WHERE id=%s", (item_id))
            conn.commit()
            rv = cursor.fetchall()
            print(rv)
            
            response = {
                "statusCode": 200,
                "headers": {},
                "body": "deleted item"
            }
            
            return response
    response = {
        "statusCode": 501,
        "headers": {},
        "body": "something went wrong"
    }
    
    return response
    
def format_db_output(row_headers, rv):
    json_data = []
    for row in rv:
        row_data = []
        for data in row:
            if type(data) is Decimal:
                row_data.append("%.2f" % float(Decimal(data).quantize(Decimal('.01'))))
            else:
                row_data.append(str(data))
        json_data.append(dict(zip(row_headers,row_data)))
    output_json = (json.dumps(json_data)) 
    return output_json