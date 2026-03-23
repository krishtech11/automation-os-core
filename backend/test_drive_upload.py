from app.workflows.invoice_sync import InvoiceSyncWorkflow
from pathlib import Path
import tempfile

workflow = InvoiceSyncWorkflow()
workflow.authenticate()

# Create test folder
print("Creating test folder in Drive...")
folder_id = workflow.create_drive_folder('UAOS_Test_Invoices')
print(f"Folder ID: {folder_id}")

# Create test file (cross-platform safe)
temp_dir = Path(tempfile.gettempdir())
test_file = temp_dir / "test_invoice.txt"

test_file.write_text("This is a test invoice\nAmount: $100\nDate: 2026-02-19")

# Upload
print("\nUploading test file...")
with open(test_file, 'rb') as f:
    data = f.read()

file_id, link = workflow.upload_to_drive('test_invoice.txt', data, folder_id)

print(f"\n✅ File uploaded!")
print(f"File ID: {file_id}")
print(f"Link: {link}")
print("\nCheck your Google Drive!")