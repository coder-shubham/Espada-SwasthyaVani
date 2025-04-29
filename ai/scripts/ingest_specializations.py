import json
import sys
sys.path.append('.')

from factory.config import FactoryConfig
from utils.vectorstores.weav8 import WeaviateCollectionClient

if __name__ == '__main__':
    SPECIALIZATIONS_COLL_NAME = "specialization"
    coll = WeaviateCollectionClient(db_client=FactoryConfig.vector_db_client, name=SPECIALIZATIONS_COLL_NAME, embeddings=FactoryConfig.embeddings)
    coll.load_collection()
    coll.delete_collection()
    coll.load_collection()

    with open('pipeline/triage/triage.json', 'r') as handle:
        triage_data = json.load(handle)

    doctor_specializations = triage_data.get('symptomTriageModule').get('doctorSpecializations')

    for ds in doctor_specializations:
        specialization = ds.get('specialization')
        description = ds.get('description')
        triage_indicators = ds.get('triageIndicators')
        properties = {'specialization': specialization, 'description': description, 'triage_indicators': triage_indicators}
        
        for ind in triage_indicators:
            vector = FactoryConfig.embeddings.encode(ind).tolist()
            coll.insert(properties=properties, vector=vector)
        
        vector = FactoryConfig.embeddings.encode(description).tolist()
        coll.insert(properties=properties, vector=vector)
        
        description_with_triage_indicators = description + '\n\n' + '\n'.join(triage_indicators)
        vector = FactoryConfig.embeddings.encode(description_with_triage_indicators).tolist()
        coll.insert(properties=properties, vector=vector)
    
    FactoryConfig.vector_db_client.close()

