import base64
import functions_framework
import json
import uuid
import os
from google.cloud import storage
import mysql.connector
from mysql.connector import Error
import logging
from google.cloud import compute_v1

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

def check_compute_instance_exists(project_id, zone, instance_name):
    """Check if a compute instance exists and is running"""
    try:
        instance_client = compute_v1.InstancesClient()
        instance = instance_client.get(
            project=project_id,
            zone=zone,
            instance=instance_name
        )
        return instance.status == "RUNNING"
    except Exception as e:
        logger.info(f"Compute instance check failed: {e}")
        return False

@functions_framework.cloud_event
def handle_bucket_creation(cloud_event):
    """Handle Cloud Storage bucket creation events from Audit Logs"""
    try:
        data = cloud_event.data
        logger.info(f"Received event data: {data}")

        # Get project_id and zone from environment variables
        project_id = os.getenv("PROJECT_ID")
        zone = os.getenv("COMPUTE_ZONE", "us-central1-a")

        if not project_id:
            raise ValueError("PROJECT_ID environment variable is required")

        # Add check for file upload to output bucket
        if isinstance(data, dict) and data.get('protoPayload', {}).get('methodName') == 'storage.objects.create':
            resource_name = data['protoPayload'].get('resourceName', '')
            bucket_name = resource_name.split('/')[3] if resource_name else ''
            
            if bucket_name.startswith('output-user-bucket-'):
                user_id = bucket_name.split('-')[3]
                compute_instance_name = f"cynthus-compute-instance-{user_id}"
                if check_compute_instance_exists(project_id, zone, compute_instance_name):
                    update_instance_state(user_id, compute_instance_name, 'ACTIVE')
                    logger.info(f"Marked instance {compute_instance_name} as ACTIVE")
                return

        # Check for compute instance termination events
        if isinstance(data, dict) and data.get('jsonPayload', {}).get('event_type') in [
            'compute.instances.delete', 
            'compute.instances.stop'
        ]:
            instance_name = data.get('resource', {}).get('labels', {}).get('instance_name', '')
            if instance_name.startswith('cynthus-compute-instance-'):
                user_id = instance_name.split('-')[-1]
                update_instance_state(user_id, instance_name, 'DEAD')
                logger.info(f"Marked instance {instance_name} as DEAD")
                return

        # Modify the compute instance creation check
        if isinstance(data, dict) and data.get('jsonPayload', {}).get('event_type') == 'compute.instances.insert':
            instance_name = data.get('resource', {}).get('labels', {}).get('instance_name', '')
            if instance_name.startswith('cynthus-compute-instance-'):
                user_id = instance_name.split('-')[-1]
                storage_client = storage.Client()
                bucket_name = f"user-bucket-{user_id}"
                output_bucket_name = f"output-user-bucket-{user_id}"
                
                try:
                    # Check all required resources exist
                    storage_client.get_bucket(bucket_name)
                    storage_client.get_bucket(output_bucket_name)
                    if check_compute_instance_exists(project_id, zone, instance_name):
                        create_deploying_entry(user_id, bucket_name, output_bucket_name, instance_name)
                    else:
                        logger.info(f"Compute instance {instance_name} not running yet")
                except Exception as e:
                    logger.info(f"Resources not ready yet for {user_id}: {e}")
                return

        # Modify the bucket creation check
        if isinstance(data, dict) and 'protoPayload' in data:
            resource_name = data['protoPayload'].get('resourceName', '')
            bucket_name = resource_name.split('/')[-1] if resource_name else ''
            
            if bucket_name.startswith('user-bucket-'):
                user_id = bucket_name.split('-')[2]
                output_bucket_name = f"output-{bucket_name}"
                compute_instance_name = f"cynthus-compute-instance-{user_id}"
                
                try:
                    # Check all required resources exist
                    storage_client = storage.Client()
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
                    
                    # Check if compute instance exists and is running
                    if check_compute_instance_exists(project_id, zone, compute_instance_name):
                        create_deploying_entry(user_id, bucket_name, output_bucket_name, compute_instance_name)
                    else:
                        logger.info(f"Compute instance {compute_instance_name} not running yet")
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

def update_instance_state(user_id, instance_name, new_state):
    """Helper function to create a new entry with updated state"""
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        # First get the most recent entry for this instance
        cursor.execute("""
            SELECT run_id, path_to_data, path_to_src, path_to_output 
            FROM logs 
            WHERE user_id = %s 
            AND compute_instance = %s 
            AND state != 'DEAD'
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (user_id, instance_name))
        
        result = cursor.fetchone()
        if result:
            run_id, path_to_data, path_to_src, path_to_output = result
            # Create new entry with same data but new state
            cursor.execute("""
                INSERT INTO logs (
                    user_id, run_id, path_to_data, path_to_src, 
                    path_to_output, compute_instance, state
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                run_id,
                path_to_data,
                path_to_src,
                path_to_output,
                instance_name,
                new_state
            ))
            connection.commit()
            logger.info(f"Created new entry with state {new_state} for instance {instance_name}")
    finally:
        if connection:
            connection.close()