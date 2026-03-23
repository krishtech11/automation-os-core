from app.workflows.invoice_sync import InvoiceSyncWorkflow

workflow = InvoiceSyncWorkflow()
workflow.authenticate()

# Search for emails with "invoice" or "receipt"
print("Searching Gmail for invoices...")
messages = workflow.search_gmail('invoice OR receipt', max_results=5)

print(f"\nFound {len(messages)} emails")

# Get details of first message
if messages:
    print("\nFetching details of first email...")
    message = workflow.get_message_details(messages[0]['id'])
    
    # Extract subject
    headers = message['payload']['headers']
    subject = next(h['value'] for h in headers if h['name'] == 'Subject')
    print(f"Subject: {subject}")
    
    # Check for attachments
    attachments = workflow.extract_attachments(message)
    print(f"Attachments: {len(attachments)}")
    for filename, data in attachments:
        print(f"  - {filename} ({len(data)} bytes)")