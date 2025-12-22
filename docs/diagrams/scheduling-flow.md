```mermaid
sequenceDiagram
    participant LM as League Manager
    participant R as Referee(s)

    LM->>LM: Generate Round-Robin Schedule
    loop For each round
        LM->>R: Assign Match
    end
```
