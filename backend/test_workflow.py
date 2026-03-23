from app.workflows.news_digest import NewsDigestWorkflow

workflow = NewsDigestWorkflow()
success, message, details = workflow.execute({
    'email': 'your-email@gmail.com',
    'category': 'technology',
    'country': 'us',
    'limit': 5
})

print(f"Success: {success}")
print(f"Message: {message}")
print(f"Details: {details}")