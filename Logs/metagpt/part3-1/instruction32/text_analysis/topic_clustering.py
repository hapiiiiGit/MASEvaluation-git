import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class TopicClustering:
    def __init__(self, n_clusters=5):
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.model = KMeans(n_clusters=self.n_clusters)

    def fit(self, documents):
        X = self.vectorizer.fit_transform(documents)
        self.model.fit(X)

    def predict(self, new_documents):
        X_new = self.vectorizer.transform(new_documents)
        return self.model.predict(X_new)
