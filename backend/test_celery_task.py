from app.tasks import execute_workflow_task
from app import create_app

app = create_app()

with app.app_context():
    # Execute task asynchronously
    result = execute_workflow_task.delay(1)  # task_id = 1
    
    print(f"Task submitted: {result.id}")
    print("Waiting for result...")
    
    # Wait for result (blocking)
    output = result.get(timeout=30)
    
    print(f"Result: {output}")