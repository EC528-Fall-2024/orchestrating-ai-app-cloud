import base64
import functions_framework
import json
import uuid
import os
from google.cloud import storage
import mysql.connector
from mysql.connector import Error
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Create and return a database connection"""
    try:
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME", "logs")
        db_port = int(os.getenv("DB_PORT", "3306"))

        # Validate required environment variables
        if not all([db_host, db_user, db_pass]):
            missing_vars = [var for var, val in {
                "DB_HOST": db_host,
                "DB_USER": db_user,
                "DB_PASS": db_pass
            }.items() if not val]
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        logger.info(f"Attempting TCP connection to {db_host}:{db_port}")
        
        config = {
            'host': db_host,
            'user': db_user,
            'password': db_pass,
            'database': db_name,
            'port': db_port,
            'connection_timeout': 30,
            'allow_local_infile': True,
            'raise_on_warnings': True
        }

        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            db_info = conn.get_server_info()
            logger.info(f"Successfully connected to MySQL server version {db_info}")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            database = cursor.fetchone()
            logger.info(f"Connected to database: {database}")
            cursor.close()
            return conn
        else:
            raise mysql.connector.Error("Connection created but not active")

    except mysql.connector.Error as err:
        logger.error(f"MySQL Error: {err}")
        if err.errno == 2003:  # Can't connect to server
            logger.error(f"Cannot connect to server at {db_host}:{db_port}")
            logger.error("Please verify:")
            logger.error("1. The Cloud SQL instance is running")
            logger.error("2. The private IP is correct")
            logger.error("3. VPC connector is properly configured")
            logger.error("4. Firewall rules allow the connection")
        elif err.errno == 1045:  # Access denied
            logger.error("Access denied - check credentials")
        elif err.errno == 1049:  # Unknown database
            logger.error("Database does not exist")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error args: {e.args}")
        raise

def get_next_run_id(cursor, user_id):
    """Get the next sequential run ID for a given user"""
    cursor.execute("""
        SELECT MAX(CAST(run_id AS UNSIGNED)) 
        FROM logs 
        WHERE user_id = %s
    """, (user_id,))
    last_run_id = cursor.fetchone()[0]
    return '0' if last_run_id is None else str(last_run_id + 1)

@functions_framework.cloud_event
def handle_bucket_creation(cloud_event):
    """Handle Cloud Storage bucket creation events from Audit Logs"""
    try:
        data = cloud_event.data
        logger.info(f"Received event data: {data}")

        if isinstance(data, dict) and 'protoPayload' in data:
            resource_name = data['protoPayload'].get('resourceName', '')
            bucket_name = resource_name.split('/')[-1] if resource_name else ''
            
            if bucket_name.startswith('user-bucket-'):
                user_id = bucket_name.split('-')[2]
                output_bucket_name = f"output-{bucket_name}"
                compute_instance_name = f"cynthus-compute-instance-{user_id}"
                
                # Check if both buckets and compute instance exist
                storage_client = storage.Client()
                try:
                    storage_client.get_bucket(bucket_name)
                    storage_client.get_bucket(output_bucket_name)
                    
                    # Create required paths
                    bucket = storage_client.get_bucket(bucket_name)
                    data_path_blob = bucket.blob('data/')
                    src_path_blob = bucket.blob('src/')
                    
                    if not data_path_blob.exists():
                        data_path_blob.upload_from_string('')
                    if not src_path_blob.exists():
                        src_path_blob.upload_from_string('')
                    
                    # Check if compute instance exists (you'll need to implement this)
                    # If everything exists, create DEPLOYING entry
                    create_deploying_entry(user_id, bucket_name, output_bucket_name, compute_instance_name)
                except Exception as e:
                    logger.info(f"Resources not ready yet for {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        raise

def create_deploying_entry(user_id, bucket_name, output_bucket_name, compute_instance_name):
    """Helper function to create DEPLOYING entry"""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        run_id = get_next_run_id(cursor, user_id)
        
        cursor.execute("""
            INSERT INTO logs (
                user_id, run_id, path_to_data, path_to_src, 
                path_to_output, compute_instance, state
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            run_id,
            f"gs://{bucket_name}/data/",
            f"gs://{bucket_name}/src/",
            f"gs://{output_bucket_name}/",
            compute_instance_name,
            'DEPLOYING'
        ))
        connection.commit()
        logger.info(f"Created DEPLOYING entry for user {user_id}")
    finally:
        if connection:
            connection.close()