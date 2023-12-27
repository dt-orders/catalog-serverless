from shared_code import setup_otel_tracing
import sys
import logging
import pymysql
import json
import os
from opentelemetry import trace
import azure.functions as func
from decimal import *
import pathlib
from dynatrace.opentelemetry.azure.functions import wrap_handler
from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor


@wrap_handler
def main(req: func.HttpRequest) -> func.HttpResponse:

    PyMySQLInstrumentor().instrument()
    current_span = trace.get_current_span()
    current_span.add_event("Python HTTP Trigger Function getDBContents Start")
    logger = logging.getLogger()
    logger.info('Python HTTP trigger function getDBContents Start.')
    #get current path for ssl cert
    current_path = pathlib.Path(__file__).parent.parent
    #print(current_path)
    ssl_cert_path = str(current_path /  'DigiCertGlobalRootCA.crt.pem')

     # rds settings
    user_name = os.environ["USER_NAME"]
    password = os.environ["PASSWORD"]
    rds_host = os.environ["RDS_HOST"]
    db_name = os.environ["DB_NAME"]

    # Connect to MySQL
    try:
        conn = pymysql.connect(
            host=rds_host,
            user=user_name,
            passwd=password,
            db=db_name,
            connect_timeout=5,
            ssl_ca=ssl_cert_path,
        )

    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()


    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    
    #function code from Mandy begin

    #output_json = {"error": "something went wrong"}
    #print(message)
    #body = json.loads(message["body"])
    body = req.get_json()
    

    function = body["function"]

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
            return func.HttpResponse(
                output_json,
                status_code=200
            )

    elif (function == "findById"):
        item_id = body["id"]
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, price FROM catalog WHERE id =%s", (item_id))
            row_headers=[x[0] for x in cursor.description] #this will extract row headers
            rv = cursor.fetchall()
            output_json = format_db_output(row_headers, rv)
            print (output_json)
            return func.HttpResponse(
                output_json,
                status_code=200
            )
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
            
            return func.HttpResponse(
                body="inserted",
                status_code=200
            )
           
    elif (function == "updateItemById"):
        item_id = body["id"]
        name = body["name"]
        price = body["price"]
        with conn.cursor() as cursor:
            cursor.execute("UPDATE catalog SET name=%s, price=%s WHERE id=%s", (name, price, item_id))
            conn.commit()
            rv = cursor.fetchall()
            print(rv)
            
        return func.HttpResponse(
            body="updated item",
            status_code=200
            )
    elif (function == "deleteItemById"):
        item_id = body["id"]
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM catalog WHERE id=%s", (item_id))
            conn.commit()
            rv = cursor.fetchall()
            print(rv)
            
            return func.HttpResponse(
                body="deleted item",
                status_code=200
            )
    return func.HttpResponse(
                body="something else went wrong",
                status_code=501
            )
    #function code from Mandy end   
 
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