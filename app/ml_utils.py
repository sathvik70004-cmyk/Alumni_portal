# app/ml_utils.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
# CRITICAL: We import the Alumni model here for database access
from app.models import Alumni 

def get_recommendations(current_alumnus_id, db_session):
    """
    Generates recommendations for a given alumnus based on common features (major, city, year).
    Returns a list of recommended Alumni IDs.
    """
    
    # 1. Fetch data required for analysis (All Alumni)
    # We fetch all data and will index the current user later
    alumni_data = db_session.query(Alumni.id, Alumni.major, Alumni.city, Alumni.graduation_year).all()
    
    # If not enough data exists (less than 2 users total), return empty list
    if len(alumni_data) < 2:
        return []

    # Convert query results to a Pandas DataFrame (essential for Sklearn)
    df_list = [a._asdict() for a in alumni_data]
    df = pd.DataFrame(df_list)
    
    # 2. Create a "content string" from relevant features (e.g., "Computer Science San Francisco 2025")
    df['content'] = df['major'].fillna('') + ' ' + df['city'].fillna('') + ' ' + df['graduation_year'].astype(str)
    
    # 3. Create Vectorizer (TF-IDF: Converts text features into numerical vectors)
    # This prepares the data for similarity comparison.
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['content'])
    
    # 4. Compute Similarity (Cosine Similarity: measures the angle between vectors)
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    # 5. Get Recommendations based on the current user's index
    indices = pd.Series(df.index, index=df['id']).drop_duplicates()
    
    try:
        idx = indices[current_alumnus_id]
    except KeyError:
        return [] # User not found in the dataset being analyzed

    # Get the similarity scores for the current user (using their index 'idx')
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Select the top 5 (excluding the user themselves, which is the first entry)
    sim_scores = sim_scores[1:6] 
    
    alumni_indices = [i[0] for i in sim_scores]
    
    # Return the list of recommended Alumni IDs
    return df['id'].iloc[alumni_indices].tolist()