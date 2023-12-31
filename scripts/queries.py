from neo4j import GraphDatabase, exceptions
import os
from dotenv import load_dotenv
import json


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


def get_itinerary(input):

    """
    Input: a json object with the following structure:
        {
            "origin_IATA": "MXP",
            "destination_IATA": "USH"
        }

    Output: a json object with the following structure:
        {
            "shortest_itinerary": "MXP -> EZE with Aerolineas Argentinas\nEZE -> USH with Aerolineas Argentinas\n"
        }
    """
    input = json.loads(input)
    origin_IATA = input["origin_IATA"]
    destination_IATA = input["destination_IATA"]
    origin_IATA = origin_IATA.upper()
    destination_IATA = destination_IATA.upper()

    load_dotenv()
    db = DB(os.getenv('NEO4J_URI'), os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
    query_string = f""" 
        MATCH p=shortestPath((:Airport {{IATA: "{origin_IATA}"}})-[:TO*..5]->(:Airport {{IATA: "{destination_IATA}"}}))
        UNWIND relationships(p) AS r
        MATCH (a1:Airport)-[r]->(a2:Airport)
        MATCH (airline:Airline)-[:OPERATES]->(:Route {{RouteID: r.RouteID}})
        RETURN a1.IATA AS From, a2.IATA AS To, airline.Name AS Airline, r.RouteID as RouteID
    """

    res = db.query(query_string)
    db.close()

    # Converting the result of the query to a string
    res_str = ""
    for record in res:
        res_str += f"{record['From']} -> {record['To']} with {record['Airline']}\n"
    
    json_res = {
        "shortest_itinerary": res_str
    }
    json_string = json.dumps(json_res)
    return json_string


    

