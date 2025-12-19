from services.firebase_service import FirebaseService
from dotenv import load_dotenv

load_dotenv()

def test_save():
    print("Initializing Firebase Service...")
    try:
        service = FirebaseService()
        print("Service Initialized.")
    except Exception as e:
        print(f"Failed to init service: {e}")
        return

    print("Attempting to save test data...")
    try:
        doc_id = service.save_attempt(
            user_id="dev_tester",
            subject="TestSubject",
            score=10,
            time_taken=60,
            question_data={"q": "test"},
            difficulty="Medium",
            is_correct=True
        )
        if doc_id:
            print(f"SUCCESS: Saved document with ID: {doc_id}")
            
            # Now try to read it back to confirm analytics
            print("Fetching analytics...")
            analytics = service.get_user_analytics("dev_tester")
            print(f"Analytics: {analytics}")
        else:
            print("FAILURE: save_attempt returned None")
    except Exception as e:
        print(f"Exception during save: {e}")

if __name__ == "__main__":
    test_save()
