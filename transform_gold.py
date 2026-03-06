import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="brawl_stars_db",
        port=3306
    )


def create_gold_views():
    connection = get_db_connection()
    cursor = connection.cursor()

    views = [
        ("gold_brawlers_by_class", """
            CREATE OR REPLACE VIEW gold_brawlers_by_class AS
            SELECT COALESCE(class, 'Unknown') AS class,
                   COUNT(*) AS brawler_count,
                   GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') AS brawlers
            FROM brawler
            GROUP BY class
            ORDER BY brawler_count DESC
        """),
        ("gold_brawlers_by_rarity", """
            CREATE OR REPLACE VIEW gold_brawlers_by_rarity AS
            SELECT COALESCE(rarity, 'Unknown') AS rarity,
                   COUNT(*) AS brawler_count,
                   GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') AS brawlers
            FROM brawler
            GROUP BY rarity
            ORDER BY FIELD(rarity, 'Common', 'Rare', 'Super Rare', 'Epic', 'Mythic', 'Legendary', 'Ultra Legendary', 'Unknown')
        """),
        ("gold_gadgets_per_brawler", """
            CREATE OR REPLACE VIEW gold_gadgets_per_brawler AS
            SELECT b.id, b.name, b.rarity, b.class,
                   COUNT(g.id) AS gadget_count,
                   GROUP_CONCAT(g.name SEPARATOR ', ') AS gadgets
            FROM brawler b
            LEFT JOIN gadget g ON b.id = g.brawler_id
            GROUP BY b.id, b.name, b.rarity, b.class
            ORDER BY gadget_count DESC, b.name
        """),
        ("gold_star_powers_per_brawler", """
            CREATE OR REPLACE VIEW gold_star_powers_per_brawler AS
            SELECT b.id, b.name, b.rarity, b.class,
                   COUNT(sp.id) AS star_power_count,
                   GROUP_CONCAT(sp.name SEPARATOR ', ') AS star_powers
            FROM brawler b
            LEFT JOIN star_power sp ON b.id = sp.brawler_id
            GROUP BY b.id, b.name, b.rarity, b.class
            ORDER BY star_power_count DESC, b.name
        """),
        ("gold_brawler_statistics", """
            CREATE OR REPLACE VIEW gold_brawler_statistics AS
            SELECT b.id, b.name, b.rarity, b.class,
                   COUNT(DISTINCT sp.id) AS star_power_count,
                   COUNT(DISTINCT g.id) AS gadget_count,
                   (COUNT(DISTINCT sp.id) + COUNT(DISTINCT g.id)) AS total_abilities
            FROM brawler b
            LEFT JOIN star_power sp ON b.id = sp.brawler_id
            LEFT JOIN gadget g ON b.id = g.brawler_id
            GROUP BY b.id, b.name, b.rarity, b.class
            ORDER BY total_abilities DESC, b.name
        """),
        ("gold_dashboard_summary", """
            CREATE OR REPLACE VIEW gold_dashboard_summary AS
            SELECT
                (SELECT COUNT(*) FROM brawler) AS total_brawlers,
                (SELECT COUNT(*) FROM star_power) AS total_star_powers,
                (SELECT COUNT(*) FROM gadget) AS total_gadgets,
                (SELECT COUNT(DISTINCT class) FROM brawler WHERE class IS NOT NULL) AS total_classes,
                (SELECT COUNT(DISTINCT rarity) FROM brawler WHERE rarity IS NOT NULL) AS total_rarities,
                (SELECT MAX(extraction_date) FROM bronze_raw) AS last_update
        """),
        ("gold_class_distribution", """
            CREATE OR REPLACE VIEW gold_class_distribution AS
            SELECT class,
                   COUNT(*) AS count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM brawler), 2) AS percentage
            FROM brawler
            WHERE class IS NOT NULL
            GROUP BY class
            ORDER BY count DESC
        """),
        ("gold_rarity_distribution", """
            CREATE OR REPLACE VIEW gold_rarity_distribution AS
            SELECT rarity,
                   COUNT(*) AS count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM brawler), 2) AS percentage
            FROM brawler
            WHERE rarity IS NOT NULL
            GROUP BY rarity
            ORDER BY FIELD(rarity, 'Common', 'Rare', 'Super Rare', 'Epic', 'Mythic', 'Legendary', 'Ultra Legendary')
        """)
    ]

    for name, query in views:
        cursor.execute(query)
        print(f"  Created view: {name}")

    connection.commit()
    cursor.close()
    connection.close()


def verify_gold_layer():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM gold_dashboard_summary")
    summary = cursor.fetchone()

    if summary:
        print("Gold Layer Summary:")
        print(f"  Total Brawlers:    {summary['total_brawlers']}")
        print(f"  Total Star Powers: {summary['total_star_powers']}")
        print(f"  Total Gadgets:     {summary['total_gadgets']}")
        print(f"  Total Classes:     {summary['total_classes']}")
        print(f"  Total Rarities:    {summary['total_rarities']}")
        print(f"  Last Update:       {summary['last_update']}")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    create_gold_views()
    verify_gold_layer()
