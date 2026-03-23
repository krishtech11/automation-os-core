from app.workflows.file_cleanup import FileCleanupWorkflow

workflow = FileCleanupWorkflow()

# Test config
config = {
    'folder': 'Downloads',
    'file_pattern': '*.pdf',
    'action': 'rename',
    'rename_pattern': 'date_title'
}

success, message, details = workflow.execute(config)
print(f"Success: {success}")
print(f"Message: {message}")
print(f"Details: {details}")