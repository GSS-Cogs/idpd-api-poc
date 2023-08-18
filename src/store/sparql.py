from SPARQLWrapper import SPARQLWrapper, JSON, QueryResult


def run_sparql(url: str) -> QueryResult:

    sparql = SPARQLWrapper(url)

    sparql.setQuery("""Thi is where teh query stuff will go """)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query()
    return results