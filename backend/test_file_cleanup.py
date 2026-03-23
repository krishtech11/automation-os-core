from app.workflows.file_cleanup import FileCleanupWorkflow

workflow = FileCleanupWorkflow()

# Test 1: Just scan and rename PDFs in Downloads
print("=" * 60)
print("TEST 1: Rename PDFs in Downloads")
print("=" * 60)

config = {
    'folder': 'Downloads',
    'file_pattern': '*.pdf',
    'action': 'rename',
    'rename_pattern': 'date_title'
}

success, message, details = workflow.execute(config)
print(f"\nSuccess: {success}")
print(f"Message: {message}")
print(f"Details: {details}")

# Test 2: Organize Downloads by type (creates subfolders)
print("\n" + "=" * 60)
print("TEST 2: Organize Downloads by file type")
print("=" * 60)

config = {
    'folder': 'Downloads',
    'file_pattern': '*',
    'action': 'organize',
    'organize_by_type': True
}

# Uncomment to run:
# success, message, details = workflow.execute(config)
# print(f"\nSuccess: {success}")
# print(f"Message: {message}")
# print(f"Details: {details}")