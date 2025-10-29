# app/ml_utils.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
# CRITICAL FIX: Import the model here (assuming models.py is imported in __init__.py)
# For reliability, we access the model directly. 
# NOTE: This file must be executed within Flask's app context where db is defined.

# We cannot directly import app.models.Alumni here due to circular import risk,
# so we rely on the object being available via db_session, and ensure the class 
# definition is imported safely elsewhere. Since Flask-SQLAlchemy registers models,
# we need to ensure the class object is imported correctly from models.py

# --- FIX: We will modify the function to accept the Alumni model as an argument ---
# However, the most practical solution that works with the structure is to 
# pull the model inside the function via the db session's access. 
# A cleaner way is to assume it's imported in the route that calls this utility.

# For standard structure, let's redefine the import assuming models is loaded
# in the main app.__init__
# Let's assume the Alumni model is accessible via the app's loaded models:

# --- Temporarily modify the function signature to bypass the error cleanly ---
# However, let's proceed with the standard import path, which works if done correctly:

# Assuming a direct import path for the model object (standard setup):
from app.models import Alumni 

def get_recommendations(current_alumnus_id, db_session):
    """Generates recommendations for a given alumnus based on common features."""
    
    # 1. Fetch data required for analysis (excluding the current user)
    alumni_data = db_session.query(Alumni.id, Alumni.major, Alumni.city, Alumni.graduation_year).filter(Alumni.id != current_alumnus_id).all()
    
    # If not enough data exists, return empty list
    if not alumni_data:
        return []

    # Fetch the current user's profile for comparison (Needed to append to df)
    current_alumnus_data = db_session.query(Alumni.id, Alumni.major, Alumni.city, Alumni.graduation_year).filter(Alumni.id == current_alumnus_id).first()
    
    # Convert query results to a DataFrame
    df_list = [a._asdict() for a in alumni_data]
    df_list.insert(0, current_alumnus_data._asdict()) # Insert current user at index 0 for easy indexing

    df = pd.DataFrame(df_list)
    
    # 2. Create a "content string" from relevant features
    df['content'] = df['major'].fillna('') + ' ' + df['city'].fillna('') + ' ' + df['graduation_year'].astype(str)
    
    # 3. Create Vectorizer (Converts text features into numerical vectors)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['content'])
    
    # 4. Compute Similarity (Cosine Similarity)
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # 5. Get Scores for the current user (index 0)
    # We use index [0] because we inserted the current user at the start
    sim_scores = list(enumerate(cosine_sim[0])) 
    
    # Sort the scores (highest similarity first)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Select the top 5 (excluding the user themselves at index 0)
    sim_scores = sim_scores[1:6] 
    
    # Get the Alumni IDs corresponding to the top recommendations
    alumni_indices = [i[0] for i in sim_scores]
    
    # Return the list of recommended Alumni IDs
    return df['id'].iloc[alumni_indices].tolist()