import json
import mysql.connector


def transform_bronze_to_silver():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="brawl_stars_db",
        port=3306
    )

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT payload FROM bronze_raw ORDER BY extraction_date DESC LIMIT 1")
    payload = json.loads(cursor.fetchone()["payload"])

    # Brawlify API returns brawlers under the "list" key
    brawlers = payload.get("list", [])

    for brawler in brawlers:
        brawler_id = brawler.get("id")
        name = brawler.get("name")
        rarity = brawler.get("rarity", {}).get("name")
        brawler_class = brawler.get("class", {}).get("name")

        cursor.execute(
            """
            INSERT INTO brawler (id, name, rarity, class)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                rarity = VALUES(rarity),
                class = VALUES(class)
            """,
            (brawler_id, name, rarity, brawler_class)
        )

        for star_power in brawler.get("starPowers", []):
            cursor.execute(
                "INSERT IGNORE INTO star_power (id, brawler_id, name, description) VALUES (%s, %s, %s, %s)",
                (star_power.get("id"), brawler_id, star_power.get("name"), star_power.get("description"))
            )

        for gadget in brawler.get("gadgets", []):
            cursor.execute(
                "INSERT IGNORE INTO gadget (id, brawler_id, name, description) VALUES (%s, %s, %s, %s)",
                (gadget.get("id"), brawler_id, gadget.get("name"), gadget.get("description"))
            )

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    transform_bronze_to_silver()
