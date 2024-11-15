import os
from pathlib import Path
from dotenv import load_dotenv

class SecretManager:
    def __init__(self):
        # Load .env file if it exists
        env_path = Path(__file__).parent / '.env'
        load_dotenv(env_path)

    def get_secret(self, key: str, default: str = None) -> str:
        """Get secret from environment variables"""
        value = os.environ.get(key, default)
        if value is None:
            raise ValueError(f"Required secret {key} not found in environment variables")
        return value

    def get_all_secrets(self) -> dict:
        """Get all required secrets"""
        return {
            'SSH_PUBLIC_KEY': self.get_secret('SSH_PUBLIC_KEY'),
            'PROJECT_ID': self.get_secret('PROJECT_ID'),
            'ZONE': self.get_secret('ZONE'),
        }