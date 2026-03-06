import json
import requests
import mysql.connector
from datetime import datetime, timezone


API_URL = "https://api.brawlify.com/v1/brawlers"


def extract_and_store_brawlers():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    raw_payload = response.json()

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="brawl_stars_db",
        port=3306
    )

    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO bronze_raw (source, extraction_date, payload) VALUES (%s, %s, %s)",
        ("brawl_stars", datetime.now(timezone.utc), json.dumps(raw_payload))
    )

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    extract_and_store_brawlers()
