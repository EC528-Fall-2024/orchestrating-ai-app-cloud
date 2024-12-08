from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
import yaml
import tempfile
import mysql.connector
app = FastAPI()

# Constants
USER = "cynthus"
PRIVATE_KEY = "=/path/to/key"
INVENTORY_DIR = "/path/to/inventory_files" 
vars_file_path = "/path/to/default_vars"
provision_playbook = "/path/to/playbook_dir/provision.yml"
code_update_playbook = "/path/to/playbook_dir/code-update.yml"
data_update_playbook = "/path/to/playbook_dir/data-update.yml"
container_run_playbook = "/path/to/playbook_dir/container-run.yml"
db_host = "sql_server_priv_ip"
db_user = "username"
db_pass = "password"
db_port = "change_port"
db_name = "db_name"
# Ensure the inventory directory exists
os.makedirs(INVENTORY_DIR, exist_ok=True)

class PlaybookRequest(BaseModel):
    ip: str
    hostname: str

class UpdateRequest(BaseModel):
    user_id: str

class ContainerRequest(BaseModel):
    user_id: str
    user_id_upper: str

def get_private_ip_by_uuid(uuid: str) -> str:
    """
    Fetch the private IP from the database using the provided UUID.

    :param uuid: The UUID for which the private IP is queried.
    :return: The private IP address as a string.
    """
    try:
        # Connect to the MySQL database
        db_connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name,
            port=db_port
        )
        cursor = db_connection.cursor()
        #Query the 
        cursor.execute("""
            SELECT ip_address FROM private_ip WHERE uuid = %s;
        """, (uuid,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            raise HTTPException(status_code=404, detail=f"UUID {uuid} not found in the database.")

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()

async def run_ansible_playbook_async(playbook_path: str,inventory_path: str, vars_path: str):
    """
    Runs the Ansible playbook asynchronously using the provided inventory file path.
    """
    process = await asyncio.create_subprocess_exec(
        "/home/control/.local/bin/ansible-playbook", "-i", inventory_path, playbook_path,"--extra-vars", f"@{vars_path}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(stderr.decode())

    return stdout.decode()
# create a dynamic inventory file based on private ip input
def create_temp_inventory(ip: str) -> str:
    """
    Creates a temporary inventory file for the specified IP address.

    :param ip: The IP address of the target host.
    :return: The path to the temporary inventory file.
    """
    inventory_content = {
        "all": {
            "hosts": {
                "target_instance": {
                    "ansible_host": ip,
                    "ansible_user": USER,
                    "ansible_ssh_private_key_file": PRIVATE_KEY,
                    "ansible_remote_tmp": "/tmp",
                    "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
                    "ansible_become": "yes"
                }
            }
        }
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode='w', dir=INVENTORY_DIR) as inventory_file:
        yaml.dump(inventory_content, inventory_file, default_flow_style=False)
        inventory_path = inventory_file.name
        print(f"Inventory file created at: {inventory_path}")
        return inventory_path
def create_temp_vars(vars_content: dict) -> str:
    """
    Creates a temporary vars file for Ansible playbook execution.

    :param vars_content: The variables content as a dictionary.
    :return: The path to the temporary vars file.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yml", mode='w', dir=INVENTORY_DIR) as vars_file:
        yaml.dump(vars_content, vars_file, default_flow_style=False)
        vars_path = vars_file.name
        print(f"Vars file created at: {vars_path}")
        return vars_path

#provision VM by installing Docker and other dependencies, also copy service account files stored on control node
@app.post("/provision")
async def provision_instances(request: PlaybookRequest):
    try:
        ip_address = request.ip
        host_name = request.hostname
        uuid = host_name.split('-')[-1]
         # Generate the vars.yml content
        vars_content = {
            "docker_image_name_src": f"/path/to/image-repository/{host_name}-0",
            "docker_image_tag": "latest",
            "output_user_bucket": f"output-user-bucket-{uuid}",
            "input_user_bucket": f"user-bucket-{uuid}"
            
        }
        inventory_path = create_temp_inventory(ip_address)
        vars_path = create_temp_vars(vars_content)
        try:
            result = await run_ansible_playbook_async(provision_playbook, inventory_path, vars_file_path)
            print(f"Provision playbook executed: {result}")
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail={"error": "Provision playbook failed", "details": str(e)})

        # Run the data update playbook
        try:
            result = await run_ansible_playbook_async(data_update_playbook, inventory_path, vars_path)
            print(f"Data update playbook executed: {result}")
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail={"error": "Data update playbook failed", "details": str(e)})

        # Run the code update playbook
        try:
            result = await run_ansible_playbook_async(code_update_playbook, inventory_path, vars_path)
            print(f"Code update playbook executed: {result}")
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail={"error": "Code update playbook failed", "details": str(e)})

        try:
            # Connect to the MySQL database
            db_connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_pass,
                database=db_name,
                port=db_port
            )
            cursor = db_connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS private_ip (
                    uuid VARCHAR(255) PRIMARY KEY,
                    ip_address VARCHAR(255) NOT NULL
                );
            """)
            # insert entry with user_id as key and private ip as value into database
            cursor.execute("""
                INSERT INTO private_ip (uuid, ip_address)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                ip_address = VALUES(ip_address);
            """, (uuid, ip_address))
            db_connection.commit()
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"Database error: {err}")
        finally:
            # Close the database connection
            if cursor:
                cursor.close()
            if db_connection:
                db_connection.close()
        if os.path.exists(inventory_path):
            os.remove(inventory_path)
            print(f"Temporary inventory file {inventory_path} deleted.")
        if os.path.exists(vars_path):
            os.remove(vars_path)
            print(f"Temporary vars file {vars_path} deleted.")
        return {"message": "Provisioning, data update, code update, and container run playbooks executed successfully", "ip": ip_address, "output": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# code update endpoint, accepts payload that includes uuid
@app.post("/code-update")
async def code_update(request: UpdateRequest):
    try:
        #ip_address = request.ip
        uuid = request.user_id
        ip_address = get_private_ip_by_uuid(uuid)
        # Generate the extra-vars file content for the code update playbook
        vars_content = {
            "docker_image_name_src": f"/path/to/image-repository/cynthus-compute-instance-{uuid}-0",
            "docker_image_tag": "latest",
            "output_user_bucket": f"output-user-bucket-{uuid}",
            "input_user_bucket": f"user-bucket-{uuid}"
            
        }
        
        # Create the inventory and vars files
        inventory_path = create_temp_inventory(ip_address)
        vars_path = create_temp_vars(vars_content)

        try:
            # Run the code update playbook asynchronously
            result = await run_ansible_playbook_async(
                playbook_path=code_update_playbook,
                inventory_path=inventory_path,
                vars_path=vars_path
            )
        finally:
            # Clean up the temporary files
            if os.path.exists(inventory_path):
                os.remove(inventory_path)
                print(f"Temporary inventory file {inventory_path} deleted.")
            if os.path.exists(vars_path):
                os.remove(vars_path)
            
                print(f"Temporary vars file {vars_path} deleted.")

        return {"message": "Code update playbook executed successfully", "ip": ip_address, "output": result}

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Code update playbook failed", "details": str(e)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
#endpoint to update data 
@app.post("/data-update")
async def data_update(request: UpdateRequest):
    try:
        #ip_address = request.ip
        uuid = request.user_id
        ip_address = get_private_ip_by_uuid(uuid)
        # Generate the extra-vars file content for the code update playbook
        vars_content = {
            "docker_image_name_src": f"/path/to/image-repository/cynthus-compute-instance-{uuid}-0",
            "docker_image_tag": "latest",
            "output_user_bucket": f"output-user-bucket-{uuid}",
            "input_user_bucket": f"user-bucket-{uuid}"
            
        }
        
        # Create the inventory and vars files
        inventory_path = create_temp_inventory(ip_address)
        vars_path = create_temp_vars(vars_content)

        try:
            # Run the code update playbook asynchronously
            result = await run_ansible_playbook_async(
                playbook_path=data_update_playbook,
                inventory_path=inventory_path,
                vars_path=vars_path
            )
        finally:
            # Clean up the temporary files
            if os.path.exists(inventory_path):
                os.remove(inventory_path)
                print(f"Temporary inventory file {inventory_path} deleted.")
            if os.path.exists(vars_path):
                os.remove(vars_path)
                print(f"Temporary vars file {vars_path} deleted.")

        return {"message": "Data update playbook executed successfully", "ip": ip_address, "output": result}

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Data update playbook failed", "details": str(e)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# container run endpoint
@app.post("/run")
async def run_container_run(request: ContainerRequest):
    try:
        #ip_address = request.ip
        uuid = request.user_id
        uuid_upper = request.user_id_upper
        ip_address = get_private_ip_by_uuid(uuid)
        # Generate the extra-vars file content for the code update playbook
        vars_content = {
            "docker_image_name_src": f"/path/to/image-repository/cynthus-compute-instance-{uuid}-0",
            "docker_image_tag": "latest",
            "output_user_bucket": f"output-user-bucket-{uuid}",
            "input_user_bucket": f"user-bucket-{uuid}",
            "user_id_upper": f"{uuid_upper}"
            
        }
        inventory_path = create_temp_inventory(ip_address)
        vars_path = create_temp_vars(vars_content)
        try:
            # Run the Ansible playbook asynchronously
            result = await run_ansible_playbook_async(container_run_playbook, inventory_path, vars_path)
        finally:
            # Clean up the inventory file after execution
            os.remove(inventory_path)
            
            print(f"Temporary inventory file {inventory_path} deleted.")
            os.remove(vars_path)
            print(f"Temporary vars file {vars_path} deleted.")

        return {"message": "Container run playbook executed successfully", "ip": ip_address, "output": result}

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Ansible playbook failed", "details": str(e)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))