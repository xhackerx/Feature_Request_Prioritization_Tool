from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from datetime import datetime

class ElasticManager:
    def __init__(self, app=None):
        self.es = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.es = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self):
        """Create the features index if it doesn't exist"""
        if not self.es.indices.exists(index='features'):
            self.es.indices.create(index='features', body={
                'mappings': {
                    'properties': {
                        'title': {'type': 'text', 'analyzer': 'standard'},
                        'description': {'type': 'text', 'analyzer': 'standard'},
                        'user_impact': {'type': 'integer'},
                        'effort_required': {'type': 'integer'},
                        'strategic_alignment': {'type': 'integer'},
                        'priority_score': {'type': 'float'},
                        'created_date': {'type': 'date'},
                        'predicted_impact': {'type': 'float'},
                        'estimated_hours': {'type': 'float'},
                        'complexity_score': {'type': 'integer'}
                    }
                }
            })

    def index_feature(self, feature):
        """Index a feature in Elasticsearch"""
        doc = {
            'title': feature.title,
            'description': feature.description,
            'user_impact': feature.user_impact,
            'effort_required': feature.effort_required,
            'strategic_alignment': feature.strategic_alignment,
            'priority_score': feature.priority_score,
            'created_date': feature.created_date.isoformat(),
            'predicted_impact': feature.predicted_impact,
            'estimated_hours': feature.estimated_hours,
            'complexity_score': feature.complexity_score
        }
        
        self.es.index(index='features', id=feature.id, body=doc)

    def search_features(self, query, filters=None, sort_by=None):
        """Search features with advanced filtering and sorting"""
        search_body = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'multi_match': {
                                'query': query,
                                'fields': ['title^2', 'description']
                            }
                        }
                    ]
                }
            }
        }

        if filters:
            search_body['query']['bool']['filter'] = []
            for field, value in filters.items():
                if isinstance(value, (tuple, list)) and len(value) == 2:
                    search_body['query']['bool']['filter'].append({
                        'range': {
                            field: {
                                'gte': value[0],
                                'lte': value[1]
                            }
                        }
                    })
                else:
                    search_body['query']['bool']['filter'].append({
                        'term': {field: value}
                    })

        if sort_by:
            search_body['sort'] = [{field: {'order': order}} 
                                 for field, order in sort_by.items()]

        results = self.es.search(index='features', body=search_body)
        return results['hits']['hits']

    def delete_feature(self, feature_id):
        """Delete a feature from the index"""
        try:
            self.es.delete(index='features', id=feature_id)
        except NotFoundError:
            pass

    def reindex_all(self, features):
        """Reindex all features"""
        self.es.indices.delete(index='features', ignore=[404])
        self._create_index_if_not_exists()
        
        for feature in features:
            self.index_feature(feature)