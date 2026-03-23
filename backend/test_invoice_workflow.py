from app.workflows.invoice_sync import InvoiceSyncWorkflow

workflow = InvoiceSyncWorkflow()

config = {
    'gmail_filter': 'has:attachment (invoice OR receipt OR bill)',
    'drive_folder': 'Invoices',
    'organize_by_date': True,
    'max_emails': 5
}

print("=" * 60)
print("INVOICE SYNC WORKFLOW TEST")
print("=" * 60)
print(f"Gmail filter: {config['gmail_filter']}")
print(f"Drive folder: {config['drive_folder']}")
print(f"Organize by date: {config['organize_by_date']}")
print("\nExecuting workflow...\n")

success, message, details = workflow.execute(config)

print(f"\nSuccess: {success}")
print(f"Message: {message}")
print(f"\nDetails:")
print(f"  Emails processed: {details.get('emails_processed', 0)}")
print(f"  Attachments uploaded: {details.get('attachments_uploaded', 0)}")

if details.get('files'):
    print(f"\nUploaded files:")
    for file in details['files']:
        print(f"  - {file['filename']}")
        print(f"    Link: {file['link']}")

print("\n✅ Check your Google Drive!")
print("Path: My Drive → Invoices → 2026 → 02 - February")