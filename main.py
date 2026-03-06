from extract_bronze import extract_and_store_brawlers
from transform_silver import transform_bronze_to_silver
from transform_gold import create_gold_views, verify_gold_layer
from visualize_gold import generate_all_visualizations


print("Brawl Stars Data Mining Pipeline")
print("Bronze -> Silver -> Gold -> Visualization")
print()

print("Step 1: Extract data from API (Bronze layer)")
extract_and_store_brawlers()
print("Done.")
print()

print("Step 2: Normalize data into tables (Silver layer)")
transform_bronze_to_silver()
print("Done.")
print()

print("Step 3: Create analytical views (Gold layer)")
create_gold_views()
print()
verify_gold_layer()
print()

print("Step 4: Generate charts and dashboard")
generate_all_visualizations()
print()

print("Pipeline complete.")
print("Open visualizations/interactive_dashboard.html in your browser.")
