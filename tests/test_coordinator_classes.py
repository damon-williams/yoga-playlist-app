import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import CoordinatorAgent

def test_coordinator_classes():
    print("=== Testing Coordinator Class Listing ===")
    
    try:
        coordinator = CoordinatorAgent()
        print("✅ Coordinator initialized")
        
        classes_text = coordinator.list_available_classes()
        print(f"\nClasses response:")
        print(f"Type: {type(classes_text)}")
        print(f"Content: {repr(classes_text)}")
        print(f"Length: {len(classes_text) if classes_text else 'None'}")
        
        if classes_text:
            print(f"\nFormatted output:")
            print(classes_text)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coordinator_classes()