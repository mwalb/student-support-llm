from llm_client import ask_llm

def test_llm():
    print("=" * 50)
    print("Testing LLM Connection")
    print("=" * 50)
    
    # Test base model
    print("\n🟦 Testing Base Model (llama3.2:1b):")
    print("-" * 40)
    response = ask_llm("What is a university library?", model="llama3.2:1b")
    print(f"Response: {response[:200]}...")
    
    # Test custom model
    print("\n🟨 Testing Custom Model (uni-assistant):")
    print("-" * 40)
    response = ask_llm("What is a university library?", model="uni-assistant")
    print(f"Response: {response[:200]}...")
    
    # Test off-topic question
    print("\n🟥 Testing Off-Topic Question:")
    print("-" * 40)
    response = ask_llm("What is a cow?", model="uni-assistant")
    print(f"Response: {response}")

if __name__ == "__main__":
    test_llm()
