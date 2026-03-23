from app.core.llm_planner_free import FreeLLMPlanner

planner = FreeLLMPlanner()

# Check if Ollama is running
if not planner.check_ollama_available():
    print("❌ Ollama is not running!")
    print("Start it with: ollama serve")
    exit(1)

print("✅ Ollama is running!")
print(f"Using model: {planner.model}")
print()

# Test queries
test_queries = [
    "Send me tech news every day at 6 PM",
    "Clean my Downloads folder every Monday morning",
    "Sync Gmail invoices to Drive weekly",
]

for query in test_queries:
    print(f"📝 Query: {query}")
    print("-" * 60)
    
    try:
        plan, confidence = planner.plan_workflow(query)
        
        print(f"✅ Success!")
        print(f"   Analysis: {plan['analysis']}")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Schedule: {plan['schedule']}")
        print(f"   Steps: {len(plan['steps'])}")
        
        for step in plan['steps']:
            print(f"\n   Step {step['step_number']}: {step['workflow_type']}")
            print(f"   → {step['description']}")
            print(f"   → Config: {step['config']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()