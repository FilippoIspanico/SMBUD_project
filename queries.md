## Data loading
To load the countries:

```
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/FilippoIspanico/SMBUD_project/master/data/countries.dat" AS row
CREATE (:Country {Name: row.Name, Iso_code: row.Iso_code, Dafif_code: row.Dafif_code})
```





To load the airports:
```
LOAD CSV WITH HEADERS FROM 'https://raw.githubusercontent.com/FilippoIspanico/SMBUD_project/master/data/airports-extended.dat' AS line
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
LOAD CSV WITH HEADERS FROM "https://raw.githubusercontent.com/FilippoIspanico/SMBUD_project/master/data/airlines.dat" AS row
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
CALL apoc.periodic.iterate(
"LOAD CSV WITH HEADERS FROM  'https://raw.githubusercontent.com/FilippoIspanico/SMBUD_project/master/data/routes_id.dat' AS row
WITH row
WHERE row.SourceAirportID IS NOT NULL AND row.SourceAirportID <> '\\N'
AND row.DestinationAirportID IS NOT NULL AND row.DestinationAirportID <> '\\N'
AND row.AirlineID IS NOT NULL AND row.AirlineID <> '\\N'
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
"
{batchSize:2, parallel:false}
)
```



TO LOAD THE ROUTES ON AURA:

```
CALL apoc.periodic.iterate(
"LOAD CSV WITH HEADERS FROM  'https://raw.githubusercontent.com/FilippoIspanico/SMBUD_project/master/data/routes_id.dat' AS row
WITH row
WHERE row.SourceAirportID IS NOT NULL AND row.SourceAirportID <> '\\N'
AND row.DestinationAirportID IS NOT NULL AND row.DestinationAirportID <> '\\N'
AND row.AirlineID IS NOT NULL AND row.AirlineID <> '\\N'
RETURN row
","
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
",
{batchSize:2, parallel:false}
)
```


## Queries

### Most Competed Routes

```
MATCH (r:Route)<-[:OPERATES]-(airline:Airline {Active: "Y"})
MATCH (:Country {Name : "Spain"})<-[:IN_COUNTRY]-(a0:Airport)<-[:DEPARTS_IN]-(r)-[:ARRIVES_IN]->(a1:Airport)
RETURN a0.City as Origin, a0.IATA as OriginAirport, a1.City as Destination, a1.IATA as DestinationAirport , count(DISTINCT airline) as OpAirlines, COLLECT(DISTINCT airline.Name) as AirlineNames
ORDER BY OpAirlines DESC
LIMIT 5
```

### ShortesPath
```
MATCH p=shortestPath((:Airport {IATA:"LMP"})-[:TO*..5]->(:Airport {IATA: "USH"}))
UNWIND relationships(p) AS r
MATCH (a1:Airport)-[r]->(a2:Airport)
MATCH (airline:Airline)-[:OPERATES]->(:Route {RouteID: r.RouteID})
RETURN a1.IATA AS From, a2.IATA AS To, airline.Name AS Airline, r.RouteID as RouteID


```

### ShortesPath with condition
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
    
### Biggest airline by countries served

```
MATCH (c0:Country)<-[:BASED_IN]-(a:Airline)-[:OPERATES]->(r:Route)-[:ARRIVES_IN]-(:Airport)-[:IN_COUNTRY]->(c:Country)
WHERE c <> c0
RETURN a.Name as Airline, COUNT (DISTINCT c) as CountryServed
ORDER BY CountryServed DESC
LIMIT 5
```

### Biggest airlines by number of destinations
```
MATCH (a:Airline)-[:OPERATES]->(r:Route)-[:ARRIVES_IN]->(a1:Airport)
RETURN a.Name as Airline, COUNT (DISTINCT a1) as NumDestinations
ORDER BY NumDestinations DESC
LIMIT 5
```

### Highest airport
```
MATCH (a:Airport)-[:IN_COUNTRY]->(c:Country)
WHERE (a.Altitude>6562)
RETURN c.Name as Coutry, a.IATA as Airport, max(a.Altitude) as Altitude 
ORDER BY Altitude DESC
LIMIT 1 
```

### Top 5 Airport by number of destinations
```
MATCH (c:Country)<-[:IN_COUNTRY]-(a:Airport)-[r:TO]->(destination:Airport)
RETURN c.Name as Country, a.IATA as Airport, a.City as City, count(DISTINCT destination) as NumDestination
ORDER BY NumRoutes DESC
LIMIT 5
```

### Top 5 country by number of operating airlines (and Italy)
```
MATCH (c:Country)<-[:BASED_IN]-(a:Airline)
WHERE a.Active = 'Y'
RETURN c.Name as Country, COUNT (DISTINCT a) as NumOperatingAirlines 
ORDER BY NumOperatingAirlines DESC
LIMIT 5
UNION MATCH (c:Country)<-[:BASED_IN]-(a:Airline)
WHERE a.Active = 'Y' and c.Name = 'Italy'
RETURN c.Name as Country, COUNT (DISTINCT a) as NumOperatingAirlines 
```

### Top 5 flight dependant countries
```
MATCH (c:Country)<-[:IN_COUNTRY]-(:Airport)-[r:TO]-(:Airport)-[:IN_COUNTRY]->(c)
RETURN c.Name as Country, count (DISTINCT r) as NumInternalRoutes
ORDER BY NumInternalRoutes DESC
LIMIT 5
```


### Underserved routes

```
MATCH(c:Country {Name: "United States"})<-[:IN_COUNTRY]-(A:Airport)-[ab:TO]->(B:Airport)-[bc:TO]->(C:Airport)-[:IN_COUNTRY]->(c)
MATCH (B)-[:IN_COUNTRY]->(c)
WHERE NOT (A)--(C) AND A <> C 
WITH A, B, C, COUNT(ab) as AB, COUNT(bc) as BC
RETURN A.Name as from, A.IATA as from_IATA, B.Name as stop, B.IATA as stop_IATA,C.Name as to ,C.IATA as to_IATA, AB as IntRoutes, BC as FinRoutes, AB + BC as TOT
ORDER BY TOT
LIMIT 5
```

### Personal notes
TO DUMP THE DB :

```
sudo neo4j-admin  dump --to=/home/filippo/neodump
```
