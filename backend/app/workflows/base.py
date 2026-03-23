"""
Base class for all workflows
"""
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class WorkflowBase(ABC):
    """
    Abstract base class for all workflows
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, config):
        """
        Execute the workflow
        Args:
            config (dict): Workflow configuration
        Returns:
            tuple: (success: bool, message: str, details: dict)
        """
        pass
    
    def log_info(self, message):
        logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message):
        logger.error(f"[{self.name}] {message}")
    
    def validate_config(self, config, required_fields):
        """
        Validate that config contains all required fields
        """
        missing = [field for field in required_fields if field not in config]
        if missing:
            raise ValueError(f"Missing required config fields: {missing}")