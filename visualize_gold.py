import os
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="brawl_stars_db",
        port=3306
    )


def fetch(query):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return pd.DataFrame(rows)


def generate_all_visualizations():
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)

    # --- Chart 1: Brawlers by Class ---
    df_class = fetch("SELECT * FROM gold_brawlers_by_class")
    if not df_class.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        colors = sns.color_palette("husl", len(df_class))
        ax1.barh(df_class['class'], df_class['brawler_count'], color=colors)
        ax1.set_xlabel('Number of Brawlers')
        ax1.set_title('Brawlers by Class')
        ax2.pie(df_class['brawler_count'], labels=df_class['class'], autopct='%1.1f%%', colors=colors)
        ax2.set_title('Brawlers by Class - Distribution')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/brawlers_by_class.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("  Saved: brawlers_by_class.png")

    # --- Chart 2: Brawlers by Rarity ---
    df_rarity = fetch("SELECT * FROM gold_brawlers_by_rarity")
    if not df_rarity.empty:
        rarity_colors = {
            'Common': '#A0A0A0',
            'Rare': '#00CC44',
            'Super Rare': '#0080FF',
            'Epic': '#800080',
            'Mythic': '#FF00FF',
            'Legendary': '#FFD700',
            'Ultra Legendary': '#FF4500'
        }
        colors = [rarity_colors.get(r, '#808080') for r in df_rarity['rarity']]
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(df_rarity['rarity'], df_rarity['brawler_count'], color=colors, edgecolor='black')
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h, str(int(h)), ha='center', va='bottom')
        ax.set_xlabel('Rarity')
        ax.set_ylabel('Number of Brawlers')
        ax.set_title('Brawler Distribution by Rarity')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/brawlers_by_rarity.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("  Saved: brawlers_by_rarity.png")

    # --- Chart 3: Abilities Analysis ---
    df_stats = fetch("SELECT * FROM gold_brawler_statistics")
    if not df_stats.empty:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        top10 = df_stats.nlargest(10, 'total_abilities')
        axes[0, 0].barh(top10['name'], top10['total_abilities'], color='#FF6B35')
        axes[0, 0].set_title('Top 10 Brawlers by Total Abilities')
        axes[0, 0].invert_yaxis()

        sp_counts = df_stats['star_power_count'].value_counts().sort_index()
        axes[0, 1].bar(sp_counts.index.astype(str), sp_counts.values, color='#4ECDC4')
        axes[0, 1].set_title('Star Power Distribution')

        gadget_counts = df_stats['gadget_count'].value_counts().sort_index()
        axes[1, 0].bar(gadget_counts.index.astype(str), gadget_counts.values, color='#95E1D3')
        axes[1, 0].set_title('Gadget Distribution')

        axes[1, 1].scatter(df_stats['star_power_count'], df_stats['gadget_count'], alpha=0.6)
        axes[1, 1].set_xlabel('Star Powers')
        axes[1, 1].set_ylabel('Gadgets')
        axes[1, 1].set_title('Star Powers vs Gadgets')

        plt.tight_layout()
        plt.savefig(f"{output_dir}/abilities_analysis.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("  Saved: abilities_analysis.png")

    # --- Chart 4: Heatmap (rarity x class) ---
    df_heat = fetch("""
        SELECT rarity, class, AVG(total_abilities) as avg_abilities
        FROM gold_brawler_statistics
        WHERE rarity IS NOT NULL AND class IS NOT NULL
        GROUP BY rarity, class
    """)
    if not df_heat.empty:
        df_heat['avg_abilities'] = df_heat['avg_abilities'].astype(float)
        pivot = df_heat.pivot(index='rarity', columns='class', values='avg_abilities')
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt='.1f', cmap='YlOrRd', linewidths=0.5)
        plt.title('Average Abilities by Rarity and Class')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/heatmap_abilities.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("  Saved: heatmap_abilities.png")

    # --- Interactive Dashboard (Plotly) ---
    if not df_stats.empty:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Brawlers by Class', 'Brawlers by Rarity',
                            'Top 15 by Total Abilities', 'Star Powers vs Gadgets'),
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'scatter'}]]
        )

        fig.add_trace(go.Pie(labels=df_class['class'], values=df_class['brawler_count'], hole=0.3), row=1, col=1)
        fig.add_trace(go.Bar(x=df_rarity['rarity'], y=df_rarity['brawler_count'], marker_color='lightblue'), row=1, col=2)

        top15 = df_stats.nlargest(15, 'total_abilities')
        fig.add_trace(go.Bar(x=top15['total_abilities'], y=top15['name'], orientation='h', marker_color='coral'), row=2, col=1)
        fig.add_trace(go.Scatter(
            x=df_stats['star_power_count'], y=df_stats['gadget_count'],
            mode='markers', text=df_stats['name'],
            marker=dict(size=10, color=df_stats['total_abilities'], colorscale='Viridis', showscale=True)
        ), row=2, col=2)

        fig.update_layout(
            title_text="Brawl Stars - Analytics Dashboard",
            showlegend=False,
            height=900,
            width=1400
        )

        fig.write_html(f"{output_dir}/interactive_dashboard.html")
        print("  Saved: interactive_dashboard.html")

    # --- Summary Report ---
    df_summary = fetch("SELECT * FROM gold_dashboard_summary")
    if not df_summary.empty:
        s = df_summary.iloc[0]
        report = f"""
========================================
BRAWL STARS DATA MINING - SUMMARY REPORT
========================================

Generated:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Last Update: {s['last_update']}

Total Brawlers:    {s['total_brawlers']}
Total Star Powers: {s['total_star_powers']}
Total Gadgets:     {s['total_gadgets']}
Total Classes:     {s['total_classes']}
Total Rarities:    {s['total_rarities']}

Avg Star Powers/Brawler: {s['total_star_powers'] / s['total_brawlers']:.2f}
Avg Gadgets/Brawler:     {s['total_gadgets'] / s['total_brawlers']:.2f}

========================================
"""
        with open(f"{output_dir}/summary_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
        print(report)
        print("  Saved: summary_report.txt")


if __name__ == "__main__":
    generate_all_visualizations()
