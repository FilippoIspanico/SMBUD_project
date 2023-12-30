
To load the countries:
```
LOAD CSV WITH HEADERS FROM "file:///countries.dat" AS row
CREATE (:Country {Name: row.Name, Iso_code: row.Iso_code, Dafif_code: row.Dafif_code})
```




To load the airports:
```
LOAD CSV WITH HEADERS FROM 'file:///airports-extended.dat' AS line
MERGE (country:Country {Name: line.Country})
CREATE (airport:Airport {
    AirportID: toInteger(line.AirportID),
    Name: line.Name,
    City: line.City,
    IATA: line.IATA,
    ICAO: line.ICAO,
    Latitude: toFloat(line.Latitude),
    Longitude: toFloat(line.Longitude),
    Altitude: toInteger(line.Altitude),
    Timezone: line.Timezone,
    DST: line.DST,
        TzDatabaseTimezone: line.TzDatabaseTimezone,
        Type: line.Type,
    Source: line.Source
})
CREATE (airport)-[:IN_COUNTRY]->(country)
```

To load the airlines:

```
LOAD CSV WITH HEADERS FROM "file:///airlines.dat" AS row
WITH row
WHERE row.Country IS NOT NULL AND row.Country <> "\\N"
MERGE (country:Country {Name: row.Country})
WITH row, country
CREATE (airline:Airline {
    AirlineID : toInteger(row.AirlineID),
    Name : row.Name,
    Alias : row.Alias,
    IATA : row.IATA,
    ICAO : row.ICAO,
    Callsign : row.Callsign,
    Active : row.Active
})
CREATE (airline)-[:BASED_IN]->(country)

```




To load the routes:
```
LOAD CSV WITH HEADERS FROM  "file:///routes_id.dat" AS row
WITH row
WHERE row.SourceAirportID IS NOT NULL AND row.SourceAirportID <> "\\N"
AND row.DestinationAirportID IS NOT NULL AND row.DestinationAirportID <> "\\N"
AND row.AirlineID IS NOT NULL AND row.AirlineID <> "\\N"
MERGE(a0:Airport {AirportID:toInteger(row.SourceAirportID)})
MERGE(a1:Airport {AirportID:toInteger(row.DestinationAirportID)})
MERGE(airline:Airline {AirlineID:toInteger(row.AirlineID)})
CREATE (a0)-[:TO {
    RouteID:toInteger(row.RouteID)
    }]->(a1)

CREATE (r:Route {

    RouteID:toInteger(row.RouteID),
    Airline:row.Airline,
    AirlineID:row.AirlineID,
    Codeshare:row.Codeshare,
    Stops:row.Stops,
    Equipment:row.Equipment
})

CREATE (a0)<-[:DEPARTS_IN]-(r)-[:ARRIVES_IN]->(a1)
CREATE (airline)-[:OPERATES]->(r)

```



QUERIES

MostCompeted Routes

```
MATCH (r:Route)<-[:OPERATES]-(airline:Airline {Active: "Y"})
MATCH (:Country {Name : "Spain"})<-[:IN_COUNTRY]-(a0:Airport)<-[:DEPARTS_IN]-(r)-[:ARRIVES_IN]->(a1:Airport)
RETURN a0.City as Origin, a0.IATA as OriginAirport, a1.City as Destination, a1.IATA as DestinationAirport , count(DISTINCT airline) as OpAirlines, COLLECT(DISTINCT airline.Name) as AirlineNames
ORDER BY OpAirlines DESC
LIMIT 5
```


A direct flight from A to B with condtion
MATCH (a0:Airport {IATA : "PMO"})-[flight:TO]->(a1:Airport {IATA: "MXP"})
MATCH (route:Route {RouteID: flight.RouteID})<-[:OPERATES]-(airline:Airline)
WHERE airline.Name = "easyJet"
RETURN airline



Shortespath
```
MATCH p=shortestPath((:Airport {IATA:"LMP"})-[:TO*..5]->(:Airport {IATA: "USH"}))
UNWIND relationships(p) AS r
MATCH (a1:Airport)-[r]->(a2:Airport)
MATCH (airline:Airline)-[:OPERATES]->(:Route {RouteID: r.RouteID})
RETURN a1.IATA AS From, a2.IATA AS To, airline.Name AS Airline, r.RouteID as RouteID


```

ShortesPath with condition
```
MATCH (airline:Airline {Name:"easyJet"})-[:OPERATES]->(r:Route)
WITH COLLECT(DISTINCT r.RouteID) as RList
MATCH p =shortestPath((a0:Airport {IATA: "MXP"})-[:TO*..5]->(a1:Airport {IATA:"ARN"}))
WHERE all(r in relationships(p) WHERE r.RouteID IN RList)
UNWIND relationships(p) AS r
MATCH (a2:Airport)-[r]->(a3:Airport)
MATCH (airline:Airline)-[:OPERATES]->(:Route {RouteID: r.RouteID})
RETURN a2.IATA as From, a3.IATA as To, airline.Name as Airline,  r.RouteID as RouteID
```

BIGGEST AIRLINE BY Countreis Served

```
MATCH (c0:Country)<-[:BASED_IN]-(a:Airline)-[:OPERATES]->(r:Route)-[:ARRIVES_IN]-(:Airport)-[:IN_COUNTRY]->(c:Country)
WHERE c <> c0
RETURN a.Name as Airline, COUNT (DISTINCT c) as CountryServed
ORDER BY CountryServed DESC
LIMIT 5
```

BIGGEST AIRLINES BY NUMBER OF DESTINATION 
```
MATCH (a:Airline)-[:OPERATES]->(r:Route)-[:ARRIVES_IN]->(a1:Airport)
RETURN a.Name as Airline, COUNT (DISTINCT a1) as NumDestinations
ORDER BY NumDestinations DESC
LIMIT 5
```
