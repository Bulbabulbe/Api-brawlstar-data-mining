# Présentation - Data Mining : Brawl Stars
## Pipeline ETL avec architecture Medallion (Bronze / Silver / Gold)

---

## PLAN (10 minutes)

1. Introduction et contexte        (1 min)
2. Source de données : l'API       (1 min)
3. Architecture Medallion          (2 min)
4. Démonstration du pipeline       (3 min)
5. Résultats et visualisations     (2 min)
6. Conclusion                      (1 min)

---

## 1. Introduction (1 min)

**Objectif du projet :**
Collecter, transformer et analyser les données de Brawl Stars (jeu mobile de Supercell)
en appliquant une architecture de data engineering professionnelle : Bronze / Silver / Gold.

**Ce qu'on fait concrètement :**
- On appelle une API pour récupérer les données des brawlers
- On les stocke brutes, puis on les normalise, puis on les agrège
- On génère des graphiques et un dashboard interactif

---

## 2. Source de données : l'API (1 min)

**API utilisée : Brawlify** (https://api.brawlify.com/v1/brawlers)
- API publique, gratuite, sans inscription
- Retourne les 102 brawlers du jeu avec leurs caractéristiques complètes

**Structure d'une réponse JSON :**
```json
{
  "list": [
    {
      "id": 16000000,
      "name": "Shelly",
      "rarity": { "name": "Common" },
      "class":  { "name": "Damage Dealer" },
      "starPowers": [ { "id": ..., "name": "Shell Shock" } ],
      "gadgets":    [ { "id": ..., "name": "Fast Forward" } ]
    }
  ]
}
```

**Ce qu'on récupère :** nom, rareté, classe, star powers, gadgets de chaque brawler.

---

## 3. Architecture Medallion (2 min)

L'architecture Medallion est un standard en data engineering.
Elle organise les données en 3 couches de qualité croissante.

```
API Brawlify
     |
     v
[ BRONZE ]  →  On stocke le JSON brut dans la table bronze_raw
                Sans modifier quoi que ce soit.
                Permet de rejouer les transformations sans rappeler l'API.
     |
     v
[ SILVER ]  →  On normalise : on découpe le JSON en tables relationnelles
                Table brawler    : 1 ligne par brawler (id, name, rarity, class)
                Table star_power : 1 ligne par star power
                Table gadget     : 1 ligne par gadget
     |
     v
[ GOLD ]    →  On crée des vues SQL analytiques
                Comptage par classe, par rareté, statistiques globales...
     |
     v
[ VIZ ]     →  Graphiques PNG + Dashboard HTML interactif (Plotly)
```

**Pourquoi cette architecture ?**
- Séparation claire des responsabilités (extraction / transformation / analyse)
- La couche Bronze garantit qu'on ne perd jamais la donnée originale
- Chaque couche est rejouable indépendamment

---

## 4. Démonstration du pipeline (3 min)

**Lancer le pipeline :**
```bash
python main.py
```

**Ce qui s'exécute :**

Etape 1 - extract_bronze.py
  - Appel HTTP GET vers l'API Brawlify
  - Stockage du JSON complet dans bronze_raw (MySQL)

Etape 2 - transform_silver.py
  - Lecture du dernier JSON depuis bronze_raw
  - INSERT dans les tables brawler, star_power, gadget
  - ON DUPLICATE KEY UPDATE : mise à jour si le brawler existe déjà

Etape 3 - transform_gold.py
  - CREATE OR REPLACE VIEW pour chaque vue analytique
  - Les vues sont des requêtes SQL sauvegardées dans MySQL

Etape 4 - visualize_gold.py
  - Requêtes sur les vues Gold
  - Génération de 4 graphiques PNG + 1 dashboard HTML

**Résultat affiché :**
```
Total Brawlers:    102
Total Star Powers: 205
Total Gadgets:     203
Total Classes:     8
Total Rarities:    7
```

---

## 5. Résultats et visualisations (2 min)

**Fichiers générés dans visualizations/ :**

| Fichier | Contenu |
|---------|---------|
| brawlers_by_class.png | Bar chart + camembert par classe |
| brawlers_by_rarity.png | Distribution par rareté avec couleurs officielles |
| abilities_analysis.png | Top 10 brawlers, distribution des capacités, scatter plot |
| heatmap_abilities.png | Heatmap rareté x classe (nb moyen de capacités) |
| interactive_dashboard.html | Dashboard interactif (zoom, hover, filtres) |
| summary_report.txt | Rapport texte avec les métriques globales |

**Points intéressants :**
- La classe la plus représentée : Damage Dealer (19 brawlers)
- La rareté la plus représentée : Mythic (38 brawlers, soit 37%)
- Presque tous les brawlers ont exactement 2 star powers et 2 gadgets

---

## 6. Conclusion (1 min)

**Ce projet couvre :**
- La collecte de données via API REST
- Le stockage brut (Bronze) pour traçabilité
- La normalisation relationnelle (Silver) : 3NF, clés étrangères
- L'agrégation analytique (Gold) : vues SQL
- La visualisation : matplotlib, seaborn, plotly

**Technologies utilisées :**
Python, MySQL/MariaDB (XAMPP), requests, pandas, matplotlib, seaborn, plotly

**L'architecture Medallion est utilisée en production chez :**
Netflix, Databricks, Airbnb — c'est un standard du data engineering moderne.

---

## Schéma de la base de données

```
bronze_raw
  id | source | extraction_date | payload (JSON)

brawler                     star_power                gadget
id | name | rarity | class  id | brawler_id | name    id | brawler_id | name
                             description               description
                               FK → brawler.id          FK → brawler.id
```

---

## Questions possibles et réponses

**Q: Pourquoi Brawlify et pas l'API officielle Brawl Stars ?**
R: L'API officielle (api.brawlstars.com) ne retourne pas les champs rarity et class
   dans l'endpoint /v1/brawlers. Brawlify est une API communautaire qui enrichit
   ces données. C'est une pratique courante en data engineering : combiner plusieurs
   sources pour obtenir des données complètes.

**Q: Qu'est-ce que le Bronze layer apporte concrètement ?**
R: Si l'API change ou devient indisponible, on peut rejouer toutes les transformations
   à partir des données brutes stockées en base. C'est la garantie de ne jamais perdre
   la donnée originale.

**Q: Pourquoi des vues SQL et pas des tables ?**
R: Les vues sont calculées à la demande. Si on rajoute des brawlers en Bronze/Silver,
   les vues Gold sont automatiquement à jour sans aucune action supplémentaire.
