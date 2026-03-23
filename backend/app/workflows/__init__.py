"""
Workflow engine for executing different automation types
"""

from .base import WorkflowBase
from .news_digest import NewsDigestWorkflow
from .file_cleanup import FileCleanupWorkflow
from .invoice_sync import InvoiceSyncWorkflow
from .document_summary import run as document_summary
from .email_report import run as email_report

# Workflow registry - maps workflow types to their classes
WORKFLOW_REGISTRY = {
    'NEWS_DIGEST': NewsDigestWorkflow,
    'FILE_CLEANUP': FileCleanupWorkflow,
    'INVOICE_SYNC': InvoiceSyncWorkflow,
}

def get_workflow(workflow_type):
    """
    Get workflow class by type
    """
    workflow_class = WORKFLOW_REGISTRY.get(workflow_type)
    if not workflow_class:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    return workflow_class()

def execute_workflow(workflow_type, task_config):
    """
    Execute a workflow with given config
    Returns: (success: bool, message: str, details: dict)
    """
    workflow = get_workflow(workflow_type)
    return workflow.execute(task_config)