import elasticsearch

es = elasticsearch.Elasticsearch()

def save_to_db(author, text, url, id_str):
    es.index(index="tweets", doc_type="tweet", id=id, body={
         "Author": author,
         "Text": text.encode('utf-8'),
         "Url": url,
         "Tweet_Id": id_str
     })


