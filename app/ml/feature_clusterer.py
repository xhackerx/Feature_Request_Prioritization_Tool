from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class FeatureClusterer:
    def __init__(self, n_clusters=5):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.clustering = KMeans(
            n_clusters=n_clusters,
            random_state=42
        )
        
    def find_similar_features(self, feature_description, existing_features, threshold=0.3):
        """Find similar features based on description similarity"""
        if not existing_features:
            return []
            
        descriptions = [feature_description] + [f.description for f in existing_features]
        vectors = self.vectorizer.fit_transform(descriptions)
        
        similarities = cosine_similarity(vectors[0:1], vectors[1:])
        similar_indices = np.where(similarities[0] > threshold)[0]
        
        return [(existing_features[i], similarities[0][i]) for i in similar_indices]
    
    def cluster_features(self, features):
        """Group features into clusters"""
        if not features:
            return []
            
        descriptions = [f.description for f in features]
        vectors = self.vectorizer.fit_transform(descriptions)
        clusters = self.clustering.fit_predict(vectors)
        
        # Calculate cluster centers for interpretation
        cluster_centers = self.clustering.cluster_centers_
        terms = self.vectorizer.get_feature_names_out()
        
        # Get top terms for each cluster
        cluster_terms = []
        for center in cluster_centers:
            top_term_indices = center.argsort()[-5:][::-1]
            cluster_terms.append([terms[i] for i in top_term_indices])
        
        # Group features by cluster
        clustered_features = {}
        for idx, cluster_id in enumerate(clusters):
            if cluster_id not in clustered_features:
                clustered_features[cluster_id] = {
                    'features': [],
                    'key_terms': cluster_terms[cluster_id]
                }
            clustered_features[cluster_id]['features'].append(features[idx])
            
        return clustered_features