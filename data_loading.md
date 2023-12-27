
To load the airlines data the following command has been executed
```
LOAD CSV WITH HEADERS FROM "file:///airlines.dat" AS row
MERGE (country:Country {name:row.Country})
CREATE (airline:Airline { AirlineID: toInteger(row.AirlineID), Name: row.Name, Alias:row.Alias, IATA:row.IATA, ICAO:row.ICAO, Callsign: row.Callsign, Active:row.Active})
CREATE (airline)-[:BASED_IN]->(country)
```

To load the airports:
```
LOAD CSV WITH HEADERS FROM 'file:///airports-extended.dat' AS line
MERGE (country:Country {name: line.Country})
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

To load the routes:

```
LOAD CSV WITH HEADERS FROM  "file:///routes.dat" AS row
WITH row
WHERE row.SourceAirportID IS NOT NULL AND row.SourceAirportID <> "\\N"
AND row.DestinationAirportID IS NOT NULL AND row.DestinationAirportID <> "\\N"
AND row.AirlineID IS NOT NULL AND row.AirlineID <> "\\N"
MERGE(a0:Airport {AirportID:toInteger(row.SourceAirportID)})
MERGE(a1:Airport {AirportID:toInteger(row.DestinationAirportID)})
MERGE(airline:Airline {AirlineID:toInteger(row.AirlineID)})
CREATE(route:Route {
    Codeshare: row.Codeshare,
    Stops: toInteger(row.Stops),
    Equipment: row.Equipment
} )
CREATE (a0)<-[:DEPARTS_AT]-(route)-[:ARRIVES_AT]->(a1)
CREATE (airline)-[:OPERATES]->(route)
```