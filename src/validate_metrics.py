import duckdb

con = duckdb.connect("db/marketing.db")

queries = {
    "totals": """
        SELECT
            SUM(spend) AS total_spend,
            SUM(clicks) AS total_clicks,
            SUM(conversions) AS total_conversions
        FROM ads_reporting;
    """,
    "platform_cpa": """
        SELECT
            platform,
            SUM(spend) AS spend,
            SUM(conversions) AS conversions,
            SUM(spend) / NULLIF(SUM(conversions), 0) AS cpa
        FROM ads_reporting
        GROUP BY 1
        ORDER BY 1;
    """,
    "google_roas": """
        SELECT
            SUM(conversion_value) / NULLIF(SUM(spend), 0) AS google_roas
        FROM ads_reporting
        WHERE platform = 'google';
    """,
    "platform_ctr": """
        SELECT
            platform,
            SUM(clicks) / NULLIF(SUM(impressions), 0) AS ctr
        FROM ads_reporting
        GROUP BY 1
        ORDER BY 1;
    """
}

for name, query in queries.items():
    print(f"\n=== {name} ===")
    print(con.execute(query).df())

con.close()