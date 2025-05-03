import sys

sys.path.append('.')

from factory.config import FactoryConfig

from utils.vectorstores.weav8 import WeaviateCollectionClient

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PlaywrightURLLoader

GOV_SCHEMES_COLL_NAME = 'gov_schemes'
GOV_SCHEMES = {
    "Free Motorized Tricycle Scheme for Persons with Disabilities - Uttar Pradesh": "https://www.myscheme.gov.in/schemes/fmtsfpwd",
    "Surakshit Matritva Aashwasan Yojana - India": "https://www.myscheme.gov.in/schemes/suman",
    "Janani Shishu Suraksha Karyakram - India": "https://www.myscheme.gov.in/schemes/jssk",
    "Medical Assistance for the Treatment of Critical Illness - Maharashtra": "https://www.myscheme.gov.in/schemes/matci",
    "Employee Health Scheme - Andhra Pradesh": "https://www.myscheme.gov.in/schemes/ehsap",
    "Dr. YSR Aarogyasri Health Insurance Scheme - Andhra Pradesh": "https://www.myscheme.gov.in/schemes/dysrhis",
    "Deen Dayal Upadhyaya Antyodaya Parivar Suraksha Yojana (DAYALU) - Haryana": "https://www.myscheme.gov.in/schemes/dayalu",
    "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana - India": "https://www.myscheme.gov.in/schemes/ab-pmjay"
}


def extract_page_text(url):
    loader = PlaywrightURLLoader(urls=[url])
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=400)
    splits = text_splitter.split_documents(docs)
    return splits

if __name__ == '__main__':
    coll = WeaviateCollectionClient(db_client=FactoryConfig.vector_db_client, name=GOV_SCHEMES_COLL_NAME, embeddings=FactoryConfig.embeddings)
    coll.load_collection()
    coll.delete_collection()

    coll.load_collection()
    
    for scheme_name, url in GOV_SCHEMES.items():
        docs = extract_page_text(url)
        
        for doc in docs:
            properties = doc.metadata
            properties['text'] = scheme_name + '\n\n ' + doc.page_content
            vector = FactoryConfig.embeddings.encode(properties['text']).tolist()
            coll.insert(properties=properties, vector=vector)
        
        print(f"Ingestion completed for Scheme({scheme_name})")
    
    
    print("Whole ingestion process is completed")
    
    FactoryConfig.vector_db_client.close()




