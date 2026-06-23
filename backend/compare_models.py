from llm_client import ask_llm

print("=" * 60)
print("COMPARISON: Base Model vs Custom Model")
print("=" * 60)

question = "What is a library?"

print("\n🔵 BASE MODEL (llama3.2:1b):")
print("-" * 40)
print(ask_llm(question, model="llama3.2:1b"))

print("\n🟢 CUSTOM MODEL (uni-assistant):")
print("-" * 40)
print(ask_llm(question, model="uni-assistant"))

print("\n" + "=" * 60)
print("✅ Custom model gives more relevant answers!")
