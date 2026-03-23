from app.workflows.invoice_sync import InvoiceSyncWorkflow

workflow = InvoiceSyncWorkflow()

print("Testing Google API authentication...")
print("A browser window will open for OAuth2 flow.")
print("")

try:
    workflow.authenticate()
    print("✅ Authentication successful!")
    print("✅ Gmail service created")
    print("✅ Drive service created")
    print("\ntoken.pickle file saved for future use")
except Exception as e:
    print(f"❌ Authentication failed: {e}")