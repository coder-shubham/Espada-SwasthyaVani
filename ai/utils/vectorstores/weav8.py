import re
import os
import sys
from weaviate.classes.query import MetadataQuery
from weaviate.classes.query import Filter
from weaviate.exceptions import WeaviateQueryError

from dotenv import load_dotenv
load_dotenv()

sys.path.append('.')
from factory.config import FactoryConfig

class WeaviateCollectionClient:
    
    def __init__(self, db_client, name, embeddings):
        self.embeddings = FactoryConfig.embeddings
        self.name = name
        self.collection = None
        self.db_client = db_client
    
    def load_collection(self):
        self.collection = self.db_client.collections.get(self.name)

    def delete_collection(self):
        self.db_client.collections.delete(self.name)
        
    def insert(self, properties, vector, uuid=None):
        if uuid:
            uuid = self.collection.data.insert(properties=properties, vector=vector, uuid=uuid)
        else:
            uuid = self.collection.data.insert(properties=properties, vector=vector)
        return str(uuid)
    
    def query_bm25(self, query, top_k=5):
        response = self.collection.query.bm25(
            query=query,
            limit=top_k,
            return_metadata=MetadataQuery(score=True, explain_score=True),
        )
        
        return self._prepare_response(response.objects)
    
    def query_vector(self, query, top_k=5):
        q_vector = list(self.embeddings.encode(query))
        
        response = self.collection.query.near_vector(
            near_vector=q_vector,
            limit=top_k,
            return_metadata=MetadataQuery(score=True, explain_score=True),
        )
        
        
        return self._prepare_response(response.objects)
    
    def query(self, query, top_k=5):
        q_vector = self.embeddings.encode(query)
        
        try:
            response =self.collection.query.hybrid(
                    query=query,
                    vector=q_vector.tolist(),
                    return_metadata=MetadataQuery(score=True, explain_score=True),
                    alpha=0.8,
                    limit=top_k
                    # target_vector="" # let's skip for now
                )            
            return self._prepare_response(response.objects)

        except WeaviateQueryError as e: # handles if collection is not present
            return []
    
    def _extract_original_score(self, explain_score):
        match = re.search(r'original score (\d+\.\d+)', explain_score)

        if match:
            original_score = float(match.group(1))
        else:
            original_score = None
        
        return original_score
    
    def _prepare_response(self, matching_instances):
        matches = list()
        for item in matching_instances:
            original_score = self._extract_original_score(item.metadata.explain_score)
            properties = item.properties

            matches.append({
                'properties': properties,
                'original_score': original_score,
                'score':  item.metadata.score
            })

        return matches


    def delete_object_with_prop(self, p_key, p_value):
        self.collection.data.delete_many(
            where=Filter.by_property(p_key).equal(p_value)
        )

    def delete_objects_by_ids(self, object_ids):
        self.collection.data.delete_many(where=Filter.by_id().contains_any(object_ids))
        
        
## run for testing purpose only
if __name__ == '__main__':
    import weaviate
    from weaviate.classes.init import Auth
    
    weaviate_api_key = os.getenv('WEAVIATE_API_KEY')
    with weaviate.connect_to_local(auth_credentials=Auth.api_key(weaviate_api_key)) as client:
        embeddings = FactoryConfig.embeddings
        coll_client = WeaviateCollectionClient(db_client=client, name="gov_schemes", embeddings=embeddings)
        coll_client.load_collection()
        
        knowledge_base_items = ['The government provides free treatment under the Ayushman Bharat scheme.', 
                'You can avail up to ₹5 lakh of health insurance coverage per family per year.'
                'This medical scheme covers both pre-existing diseases and emergency treatments.',
                'Beneficiaries can visit any empaneled hospital for cashless treatment.',
                'To apply, you need to check your eligibility using your Aadhaar card.']
        
        for item in knowledge_base_items:
            vector = embeddings.encode(item).tolist()
            properties = {'text': item}
            coll_client.insert(properties=properties, vector=vector)
            
        
        hindi_queries = [
            "आयुष्मान भारत योजना के लिए पात्रता कैसे जांचें?",
            "क्या यह योजना पहले से मौजूद बीमारियों को कवर करती है?",
            "योजना के अंतर्गत कौन-कौन से अस्पताल शामिल हैं?"
        ]
        
        marathi_queries = [
            "आयुष्मान भारत योजनेचा लाभ घेण्यासाठी पात्रता कशी तपासावी?",
            "ही योजना कोणत्या आजारांवर उपचार करते?",
            "योजनेअंतर्गत कोणते रुग्णालये समाविष्ट आहेत?"
        ]
        
        telugu_queries = [
            "ఆయుష్మాన్ భారత్ పథకానికి అర్హత ఎలా తెలుసుకోవాలి?",
            "ఈ పథకం లో ఉన్న వ్యాధులను కవర చేస్తుందా?",
            "ఈ పథకం ద్వారా చికిత్స అందించే ఆసుపత్రులు ఏవి?"
        ]
        
        print("Hindi Queries Run Test: ")
        for query in hindi_queries:
            vector = embeddings.encode(query).tolist()
            results = coll_client.query(query=query, top_k=1)
            
            print(f"Query: {query}")
            print(f"Chunk retrieved: {results[0]['properties']['text']}")
        
        print("----Hindi Tests Completed.----")
            

        print("Marathi Queries Run Test: ")
        for query in marathi_queries:
            vector = embeddings.encode(query).tolist()
            results = coll_client.query(query=query, top_k=1)
            
            print(f"Query: {query}")
            print(f"Chunk retrieved: {results[0]['properties']['text']}")   
        
        print("----Marathi Tests Completed.----")   
            
        print("Telugu Queries Run Test: ")
        for query in telugu_queries:
            vector = embeddings.encode(query).tolist()
            results = coll_client.query(query=query, top_k=1)
            
            print(f"Query: {query}")
            print(f"Chunk retrieved: {results[0]['properties']['text']}")    
        
        print("----Telugu Tests Completed.----")
        
        print("Deleting the collection after this unittest")
        # coll_client.delete_collection()
    
    
    

