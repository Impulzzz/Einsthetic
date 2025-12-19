import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class FirebaseService:
    def __init__(self):
        cred_path = os.getenv("FIREBASE_CREDENTIALS")
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def verify_token(self, id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None

    def save_attempt(self, user_id, subject, score, time_taken, question_data, difficulty="Medium", is_correct=False):
        """
        Saves a user's quiz attempt.
        """
        try:
            doc_ref = self.db.collection('attempts').document()
            doc_ref.set({
                'user_id': user_id,
                'subject': subject,
                'score': score,
                'time_taken': time_taken,
                'question_data': question_data,
                'difficulty': difficulty,
                'is_correct': is_correct,
                'timestamp': datetime.utcnow() # Use serverTimestamp in production typically
            })
            print(f"Saved attempt {doc_ref.id} for user {user_id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error saving attempt: {e}")
            return None

    def get_user_analytics(self, user_id):
        """
        Fetches aggregated data for dashboard charts and stats.
        """
        try:
            attempts_ref = self.db.collection('attempts').where('user_id', '==', user_id)
            attempts = list(attempts_ref.stream())
            
            total_attempts = len(attempts)
            correct_count = 0
            
            subject_scores = {}
            subject_counts = {}
            recent_activity = []
            
            # Simple daily counter (Last 7 days)
            daily_labels = [] # We'll generate dynamic labels on frontend or fixed here
            daily_data_map = {} # 'YYYY-MM-DD': count

            # Sort attempts by timestamp descending for recent history
            sorted_attempts = sorted(attempts, key=lambda x: x.to_dict().get('timestamp', datetime.min), reverse=True)

            for i, attempt in enumerate(sorted_attempts):
                data = attempt.to_dict()
                
                # Stats
                if data.get('is_correct'):
                    correct_count += 1
                
                # Radar Data
                subj = data.get('subject')
                score = data.get('score', 0)
                if subj:
                    subject_scores[subj] = subject_scores.get(subj, 0) + score
                    subject_counts[subj] = subject_counts.get(subj, 0) + 1
                
                # Recent Activity (Top 5)
                if i < 5:
                    ts_val = data.get('timestamp')
                    if isinstance(ts_val, datetime):
                        ts_val = ts_val.isoformat()
                    else:
                        ts_val = str(ts_val) if ts_val else None

                    recent_activity.append({
                        'subject': subj,
                        'score': score,
                        'is_correct': data.get('is_correct'),
                        'difficulty': data.get('difficulty', 'Medium'),
                        'timestamp': ts_val
                    })
                
                # Daily Progress
                ts = data.get('timestamp')
                if ts:
                    # Handle both datetime object and string if legacy
                    if isinstance(ts, datetime):
                        date_str = ts.strftime('%Y-%m-%d')
                    else:
                        date_str = str(ts)[:10] # Fallback
                        
                    daily_data_map[date_str] = daily_data_map.get(date_str, 0) + 1

            # Processing Subject Proficiency (Avg Score)
            proficiency = {}
            for subj in subject_scores:
                proficiency[subj] = round(subject_scores[subj] / subject_counts[subj], 3) # Max 2 per q usually
            
            # Processing Daily Progress (Last 7 days)
            # This logic mimics a simple "fill missing days with 0" approach
            # Using basic string keys for simplicity in JSON
            
            success_rate = round((correct_count / total_attempts) * 100, 1) if total_attempts > 0 else 0

            return {
                'total_attempts': total_attempts,
                'success_rate': success_rate,
                'proficiency': proficiency,
                'recent_activity': recent_activity,
                'daily_progress': daily_data_map, # Frontend can fill gaps
                'correct_count': correct_count
            }

        except Exception as e:
            print(f"Error fetching analytics: {e}")
            return {
                'total_attempts': 0, 'success_rate': 0, 'proficiency': {}, 'recent_activity': []
            }
