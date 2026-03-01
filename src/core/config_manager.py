"""
Configuration Manager Module
Handles application settings and credentials securely
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import dotenv


class ConfigManager:
    """Manages application configuration and credentials"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".moodle_fetcher"
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / ".key"
        self.env_file = Path.cwd() / ".env"
        
        # Create config directory
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize encryption
        self.cipher = self._get_cipher()
        
        # Load configuration
        self.config = self._load_config()
    
    def _get_cipher(self) -> Fernet:
        """Get or create encryption key"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "username": "",
            "password": "",
            "moodle_url": "https://moodlegurukul.nie.ac.in",
            "auto_login": False,
            "save_credentials": False,
            "headless": True,
            "slow_mo": 100,
            "timeout": 30,
            "data_refresh_interval": 300,  # 5 minutes
            "theme": "dark",
            "notifications_enabled": True,
            "default_export_format": "JSON"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = self.cipher.decrypt(
                            encrypted_data.encode()
                        )
                        config = json.loads(decrypted_data.decode())
                        return {**default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Try loading from .env file
        if self.env_file.exists():
            dotenv.load_dotenv(self.env_file)
            env_config = {
                "username": os.getenv("EMAIL", ""),
                "password": os.getenv("PASS", ""),
                "moodle_url": os.getenv("MOODLE_URL", default_config["moodle_url"])
            }
            return {**default_config, **env_config}
        
        return default_config
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            # Remove sensitive data if not saving credentials
            config_to_save = self.config.copy()
            if not config_to_save.get("save_credentials"):
                config_to_save["username"] = ""
                config_to_save["password"] = ""
            
            # Encrypt and save
            json_data = json.dumps(config_to_save, indent=2)
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            with open(self.config_file, 'w') as f:
                f.write(encrypted_data.decode())
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def get_credentials(self) -> tuple:
        """Get username and password"""
        return self.config.get("username", ""), self.config.get("password", "")
    
    def validate_config(self) -> tuple[bool, str]:
        """Validate configuration"""
        if not self.config.get("username"):
            return False, "Username is required"
        if not self.config.get("password"):
            return False, "Password is required"
        if not self.config.get("moodle_url"):
            return False, "Moodle URL is required"
        return True, "Configuration valid"