-- ============================================
-- BRAWL STARS DATA MINING PROJECT
-- Database Initialization Script
-- ============================================
-- Architecture: Bronze -> Silver -> Gold
-- ============================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS brawl_stars_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE brawl_stars_db;

-- ============================================
-- BRONZE LAYER: Raw Data Storage
-- ============================================

DROP TABLE IF EXISTS bronze_raw;

CREATE TABLE bronze_raw (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100) NOT NULL COMMENT 'Data source identifier (e.g., brawl_stars)',
    extraction_date DATETIME NOT NULL COMMENT 'Timestamp of data extraction',
    payload JSON NOT NULL COMMENT 'Raw JSON payload from API',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_extraction_date (extraction_date),
    INDEX idx_source (source)
) ENGINE=InnoDB
COMMENT='Bronze layer - stores raw unprocessed API data';


-- ============================================
-- SILVER LAYER: Normalized Tables
-- ============================================

-- Drop existing Silver tables (in correct order due to foreign keys)
DROP TABLE IF EXISTS gadget;
DROP TABLE IF EXISTS star_power;
DROP TABLE IF EXISTS brawler;

-- Brawler master table
CREATE TABLE brawler (
    id INT PRIMARY KEY COMMENT 'Unique brawler ID from API',
    name VARCHAR(100) NOT NULL COMMENT 'Brawler name',
    rarity VARCHAR(50) COMMENT 'Rarity level (Common, Rare, Super Rare, Epic, Mythic, Legendary, Chromatic)',
    class VARCHAR(50) COMMENT 'Brawler class/role (Tank, Support, Assassin, etc.)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_rarity (rarity),
    INDEX idx_class (class)
) ENGINE=InnoDB
COMMENT='Silver layer - normalized brawler information';

-- Star Powers table
CREATE TABLE star_power (
    id INT PRIMARY KEY COMMENT 'Unique star power ID from API',
    brawler_id INT NOT NULL COMMENT 'Reference to brawler',
    name VARCHAR(100) NOT NULL COMMENT 'Star power name',
    description TEXT COMMENT 'Star power description/effect',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brawler_id) REFERENCES brawler(id) ON DELETE CASCADE,
    INDEX idx_brawler_id (brawler_id)
) ENGINE=InnoDB
COMMENT='Silver layer - brawler star powers';

-- Gadgets table
CREATE TABLE gadget (
    id INT PRIMARY KEY COMMENT 'Unique gadget ID from API',
    brawler_id INT NOT NULL COMMENT 'Reference to brawler',
    name VARCHAR(100) NOT NULL COMMENT 'Gadget name',
    description TEXT COMMENT 'Gadget description/effect',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brawler_id) REFERENCES brawler(id) ON DELETE CASCADE,
    INDEX idx_brawler_id (brawler_id)
) ENGINE=InnoDB
COMMENT='Silver layer - brawler gadgets';


-- ============================================
-- GOLD LAYER: Analytical Views
-- ============================================

-- View: Brawlers grouped by class
CREATE OR REPLACE VIEW gold_brawlers_by_class AS
SELECT
    COALESCE(class, 'Unknown') AS class,
    COUNT(*) AS brawler_count,
    GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') AS brawlers
FROM brawler
GROUP BY class
ORDER BY brawler_count DESC;

-- View: Brawlers grouped by rarity
CREATE OR REPLACE VIEW gold_brawlers_by_rarity AS
SELECT
    COALESCE(rarity, 'Unknown') AS rarity,
    COUNT(*) AS brawler_count,
    GROUP_CONCAT(name ORDER BY name SEPARATOR ', ') AS brawlers
FROM brawler
GROUP BY rarity
ORDER BY
    FIELD(rarity, 'Common', 'Rare', 'Super Rare', 'Epic', 'Mythic', 'Legendary', 'Chromatic', 'Unknown');

-- View: Gadget count per brawler
CREATE OR REPLACE VIEW gold_gadgets_per_brawler AS
SELECT
    b.id,
    b.name,
    b.rarity,
    b.class,
    COUNT(g.id) AS gadget_count,
    GROUP_CONCAT(g.name SEPARATOR ', ') AS gadgets
FROM brawler b
LEFT JOIN gadget g ON b.id = g.brawler_id
GROUP BY b.id, b.name, b.rarity, b.class
ORDER BY gadget_count DESC, b.name;

-- View: Star Power count per brawler
CREATE OR REPLACE VIEW gold_star_powers_per_brawler AS
SELECT
    b.id,
    b.name,
    b.rarity,
    b.class,
    COUNT(sp.id) AS star_power_count,
    GROUP_CONCAT(sp.name SEPARATOR ', ') AS star_powers
FROM brawler b
LEFT JOIN star_power sp ON b.id = sp.brawler_id
GROUP BY b.id, b.name, b.rarity, b.class
ORDER BY star_power_count DESC, b.name;

-- View: Complete brawler statistics
CREATE OR REPLACE VIEW gold_brawler_statistics AS
SELECT
    b.id,
    b.name,
    b.rarity,
    b.class,
    COUNT(DISTINCT sp.id) AS star_power_count,
    COUNT(DISTINCT g.id) AS gadget_count,
    (COUNT(DISTINCT sp.id) + COUNT(DISTINCT g.id)) AS total_abilities
FROM brawler b
LEFT JOIN star_power sp ON b.id = sp.brawler_id
LEFT JOIN gadget g ON b.id = g.brawler_id
GROUP BY b.id, b.name, b.rarity, b.class
ORDER BY total_abilities DESC, b.name;

-- View: Summary dashboard metrics
CREATE OR REPLACE VIEW gold_dashboard_summary AS
SELECT
    (SELECT COUNT(*) FROM brawler) AS total_brawlers,
    (SELECT COUNT(*) FROM star_power) AS total_star_powers,
    (SELECT COUNT(*) FROM gadget) AS total_gadgets,
    (SELECT COUNT(DISTINCT class) FROM brawler WHERE class IS NOT NULL) AS total_classes,
    (SELECT COUNT(DISTINCT rarity) FROM brawler WHERE rarity IS NOT NULL) AS total_rarities,
    (SELECT MAX(extraction_date) FROM bronze_raw) AS last_update;


-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Show all tables
SHOW TABLES;

-- Show structure of each table
DESCRIBE bronze_raw;
DESCRIBE brawler;
DESCRIBE star_power;
DESCRIBE gadget;

-- Display created views
SHOW FULL TABLES WHERE Table_type = 'VIEW';

SELECT 'Database initialization completed successfully!' AS status;
