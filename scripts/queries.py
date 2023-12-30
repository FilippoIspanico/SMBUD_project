from neo4j import GraphDatabase, exceptions

class DB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def query(self, query):
        with self.driver.session() as session:
            try:
                return list(session.run(query))
            except exceptions.CypherError as e:
                print(f"An error occurred when executing the query: {e}")
            except exceptions.ServiceUnavailable as e:
                print(f"The Neo4j service is not available: {e}")





db = DB("bolt://host:7687", "neo4j", "valeria")
query_string = """ MATCH (a:Airline)-[:OPERATES]->(r:Route)-[:ARRIVES_IN]->(a1:Airport)  
                    RETURN a.Name as Airline, COUNT (DISTINCT a1) as NumDestinations 
                    ORDER BY NumDestinations DESC 
                    LIMIT 5
                    """
res = db.query(query_string)
for record in res:
    print(record)

db.close()
