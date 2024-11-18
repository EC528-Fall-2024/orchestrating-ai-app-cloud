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

@functions_framework.cloud_event
def handle_bucket_creation(cloud_event):
    """Handle Cloud Storage bucket creation events from Audit Logs"""
    try:
        # Get the event data
        data = cloud_event.data
        logger.info(f"Received event data: {data}")
        
        # For Audit Log events, the data will be in the protoPayload
        if isinstance(data, dict) and 'protoPayload' in data:
            resource_name = data['protoPayload'].get('resourceName', '')
            logger.info(f"Resource name from audit log: {resource_name}")
            # Extract bucket name from resource name
            bucket_name = resource_name.split('/')[-1] if resource_name else ''
        else:
            logger.error("Invalid event format")
            return

        logger.info(f"Processing bucket creation: {bucket_name}")

        # Only process user buckets
        if not bucket_name.startswith('user-bucket-'):
            logger.info(f"Skipping non-user bucket: {bucket_name}")
            return

        # Extract user_id from bucket name
        parts = bucket_name.split('-')
        if len(parts) >= 3:
            user_id = parts[2]  # Remove 'user_' prefix
        else:
            logger.error(f"Invalid bucket name format: {bucket_name}")
            return

        # Generate run_id without 'run_' prefix
        run_id = str(uuid.uuid4())[:8]

        # Check for output bucket
        output_bucket_name = f"output-{bucket_name}"
        storage_client = storage.Client()
        
        try:
            # Wait for output bucket to exist
            output_bucket_exists = False
            try:
                storage_client.get_bucket(output_bucket_name)
                output_bucket_exists = True
                logger.info(f"Output bucket {output_bucket_name} exists")
            except Exception as e:
                logger.info(f"Output bucket {output_bucket_name} does not exist yet")
                return  # Exit and wait for output bucket to be created

            # Only proceed if output bucket exists
            if output_bucket_exists:
                bucket = storage_client.get_bucket(bucket_name)
                data_path_blob = bucket.blob('data/')
                src_path_blob = bucket.blob('src/')
                
                # Create the paths if they don't exist
                if not data_path_blob.exists():
                    data_path_blob.upload_from_string('')
                if not src_path_blob.exists():
                    src_path_blob.upload_from_string('')
                    
                logger.info("Required paths exist or have been created")

                # Connect to database and insert record
                connection = get_db_connection()
                try:
                    # Insert only DEPLOYING state
                    cursor = connection.cursor()
                    cursor.execute("""
                        INSERT INTO logs (run_id, user_id, path_to_data, path_to_src, path_to_output, state)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        run_id,
                        user_id,
                        f"gs://{bucket_name}/data/",
                        f"gs://{bucket_name}/src/",
                        f"gs://{output_bucket_name}/",
                        'DEPLOYING'
                    ))

                    connection.commit()
                    cursor.close()
                    logger.info(f"Successfully processed bucket creation for {bucket_name}")

                except Exception as e:
                    logger.error(f"Database error: {e}")
                    raise
                finally:
                    if connection:
                        connection.close()

        except Exception as e:
            logger.error(f"Error checking/creating paths: {e}")
            raise

    except Exception as e:
        logger.error(f"Error processing event: {e}")
        raise