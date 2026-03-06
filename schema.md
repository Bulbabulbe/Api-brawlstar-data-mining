# Schema de données

## MCD - Modele Conceptuel de Données

```mermaid
erDiagram
    SOURCE_API {
        string url
        string format
    }

    BRAWLER {
        string name
        string rarity
        string class
    }

    STAR_POWER {
        string name
        string description
    }

    GADGET {
        string name
        string description
    }

    SOURCE_API ||--o{ BRAWLER : "fournit"
    BRAWLER ||--o{ STAR_POWER : "possede (0,n)"
    BRAWLER ||--o{ GADGET : "possede (0,n)"
```

---

## MLD - Modele Logique de Données

```mermaid
erDiagram
    BRONZE_RAW {
        int id PK
        string source
        date extraction_date
        string payload
        date created_at
    }

    BRAWLER {
        int id PK
        string name
        string rarity
        string class
        date created_at
        date updated_at
    }

    STAR_POWER {
        int id PK
        int brawler_id FK
        string name
        string description
        date created_at
        date updated_at
    }

    GADGET {
        int id PK
        int brawler_id FK
        string name
        string description
        date created_at
        date updated_at
    }

    BRAWLER ||--o{ STAR_POWER : "brawler_id"
    BRAWLER ||--o{ GADGET : "brawler_id"
```

---

## Regles de gestion

- Un brawler peut avoir 0, 1 ou 2 star powers
- Un brawler peut avoir 0, 1 ou 2 gadgets
- Les star powers et gadgets sont toujours rattaches a un brawler (FK obligatoire)
- La couche Bronze stocke le JSON brut sans transformation
- Les couches Silver et Gold sont construites a partir du Bronze
