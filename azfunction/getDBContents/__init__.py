import shared_code.setup_otel_tracing
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
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:

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
    #logger.info(cnx)
    # Show catalog table
    cursor = conn.cursor()
    sql_string = "select * from catalog"
    cursor.execute(sql_string)
    result_list = cursor.fetchall()
    # Build result response text
    result_str_list = []
    for row in result_list:
        row_str = ', '.join([str(v) for v in row])
        result_str_list.append(row_str)
    result_str = '\n'.join(result_str_list)
    logger.info("Returned all DB contents")
    return func.HttpResponse(
        result_str,
        status_code=200
    )
