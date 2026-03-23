from app.core.intent_parser import parse_task_intent_v2

test_cases = [
    # News examples
    "Send me top 15 tech news from India every Friday at 6 PM to abc@gmail.com",
    "Daily business news at 9:30 AM",
    "Har Monday subah mujhe sports news bhejo",
    
    # File examples
    "Clean my Downloads PDFs every 3 hours",
    "Organize Desktop images daily at 11 PM",
    "Rename Documents folder files",
    
    # Edge cases
    "Something random that doesn't match",
]

print("=" * 70)
print("ADVANCED INTENT PARSER TEST")
print("=" * 70)

for text in test_cases:
    print(f"\n📝 Input: {text}")
    workflow_type, config, schedule, confidence = parse_task_intent_v2(text)
    
    print(f"   Type: {workflow_type}")
    print(f"   Confidence: {confidence:.2%}")
    print(f"   Schedule: {schedule}")
    print(f"   Config: {config}")