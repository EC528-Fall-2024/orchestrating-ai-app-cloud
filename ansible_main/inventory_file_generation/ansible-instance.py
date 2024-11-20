from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
import yaml
import tempfile

app = FastAPI()

# Constants
USER = "your/username"
PRIVATE_KEY = "/path/to/private/key"
PLAYBOOK = "/path/to/playbook"
INVENTORY_DIR = "/path/to/inventory/dir"  

# Ensure the inventory directory exists
os.makedirs(INVENTORY_DIR, exist_ok=True)

class PlaybookRequest(BaseModel):
    ip: str
    hostname: str

async def run_ansible_playbook_async(inventory_path: str, vars_path: str):
    """
    Runs the Ansible playbook asynchronously using the provided inventory file path.
    """
    process = await asyncio.create_subprocess_exec(
        "/path/to/executable/ansible-playbook", "-i", inventory_path, PLAYBOOK,"--extra-vars", f"@{vars_path}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(stderr.decode())

    return stdout.decode()

@app.post("/run")
async def run_ansible_playbook(request: PlaybookRequest):
    try:
        ip_address = request.ip
        host_name = request.hostname
        uuid = host_name.split('-')[-1]
         # Generate the vars.yml content
        vars_content = {
            "docker_image_name_src": f"/user/image/repository/location/{host_name}-0",
            "docker_image_tag": "latest",
            "output_user_bucket": f"output-user-bucket-{uuid}"
            
        }
        # Create a temporary vars.yml file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yml", mode='w', dir=INVENTORY_DIR) as vars_file:
            yaml.dump(vars_content, vars_file, default_flow_style=False)
            vars_path = vars_file.name
            print(f"Vars file created at: {vars_path}")
        # Generate the inventory content
        inventory_content = {
            "all": {
                "hosts": {
                    "target_instance": {
                        "ansible_host": ip_address,
                        "ansible_user": USER,
                        "ansible_ssh_private_key_file": PRIVATE_KEY,
                        "ansible_remote_tmp": "/tmp",
                        "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null",
                        "ansible_become": "yes"
                       
                    }
                }
            }
        }
        # Create a temporary inventory file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml", mode='w', dir=INVENTORY_DIR) as inventory_file:
            yaml.dump(inventory_content, inventory_file, default_flow_style=False)
            inventory_path = inventory_file.name
            print(f"Inventory file created at: {inventory_path}")

        try:
            # Run the Ansible playbook asynchronously
            result = await run_ansible_playbook_async(inventory_path, vars_path)
        finally:
            # Clean up the inventory file after execution
            os.remove(inventory_path)
            print(f"Temporary inventory file {inventory_path} deleted.")

        return {"message": "Playbook executed successfully", "ip": ip_address, "output": result}

    except RuntimeError as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Ansible playbook failed", "details": str(e)},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))