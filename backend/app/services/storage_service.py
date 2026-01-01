"""
Simple file storage service to replace MinIO.
Stores reports and artifacts in local filesystem.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime

logger = logging.getLogger(__name__)


class StorageService:
    """Simple file-based storage service."""
    
    def __init__(self, base_dir: str = "./storage"):
        """
        Initialize storage service.
        
        Args:
            base_dir: Base directory for storage
        """
        self.base_dir = Path(base_dir)
        self.reports_dir = self.base_dir / "reports"
        self.artifacts_dir = self.base_dir / "artifacts"
        
        # Create directories if they don't exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Storage service initialized at {self.base_dir}")
    
    def save_report(self, filename: str, content: bytes) -> str:
        """
        Save a report file.
        
        Args:
            filename: Name of the file
            content: File content as bytes
            
        Returns:
            Path to saved file
        """
        filepath = self.reports_dir / filename
        filepath.write_bytes(content)
        logger.info(f"Saved report: {filepath}")
        return str(filepath)
    
    def save_artifact(self, filename: str, content: bytes) -> str:
        """
        Save an artifact file.
        
        Args:
            filename: Name of the file
            content: File content as bytes
            
        Returns:
            Path to saved file
        """
        filepath = self.artifacts_dir / filename
        filepath.write_bytes(content)
        logger.info(f"Saved artifact: {filepath}")
        return str(filepath)
    
    def get_report(self, filename: str) -> Optional[bytes]:
        """
        Get a report file.
        
        Args:
            filename: Name of the file
            
        Returns:
            File content as bytes, or None if not found
        """
        filepath = self.reports_dir / filename
        if filepath.exists():
            return filepath.read_bytes()
        return None
    
    def get_artifact(self, filename: str) -> Optional[bytes]:
        """
        Get an artifact file.
        
        Args:
            filename: Name of the file
            
        Returns:
            File content as bytes, or None if not found
        """
        filepath = self.artifacts_dir / filename
        if filepath.exists():
            return filepath.read_bytes()
        return None
    
    def list_reports(self) -> list[str]:
        """List all report files."""
        return [f.name for f in self.reports_dir.iterdir() if f.is_file()]
    
    def list_artifacts(self) -> list[str]:
        """List all artifact files."""
        return [f.name for f in self.artifacts_dir.iterdir() if f.is_file()]
    
    def delete_report(self, filename: str) -> bool:
        """
        Delete a report file.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if deleted, False if not found
        """
        filepath = self.reports_dir / filename
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Deleted report: {filepath}")
            return True
        return False
    
    def delete_artifact(self, filename: str) -> bool:
        """
        Delete an artifact file.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if deleted, False if not found
        """
        filepath = self.artifacts_dir / filename
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Deleted artifact: {filepath}")
            return True
        return False


# Global storage service instance
storage_service = StorageService()
