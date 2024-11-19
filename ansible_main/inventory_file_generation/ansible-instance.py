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

async def run_ansible_playbook_async(inventory_path: str):
    #path to the ansible-playbook executable obtained using "which ansible-playbook"
    process = await asyncio.create_subprocess_exec(
        "/path/to/executable/ansible-playbook", "-i", inventory_path, PLAYBOOK,
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
            result = await run_ansible_playbook_async(inventory_path)
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