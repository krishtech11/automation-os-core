from app.core.intent_parser import parse_task_intent

test_cases = [
    "Har Monday ko mujhe top 10 tech news email karna",
    "Send me daily tech news",
    "Every evening send me business news",
    "Roz shaam ko sports news bhejo",
]

for text in test_cases:
    workflow_type, config, schedule = parse_task_intent(text)
    print(f"\nInput: {text}")
    print(f"  Type: {workflow_type}")
    print(f"  Schedule: {schedule}")
    print(f"  Config: {config}")