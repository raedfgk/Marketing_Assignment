import duckdb

con = duckdb.connect("db/marketing.db")

print("\nPlatform summary:\n")
print(con.execute("""
    SELECT
        platform,
        SUM(spend) AS spend,
        SUM(impressions) AS impressions,
        SUM(clicks) AS clicks,
        SUM(conversions) AS conversions,
        SUM(conversion_value) AS conversion_value,
        SUM(clicks)::DOUBLE / NULLIF(SUM(impressions), 0) AS ctr,
        SUM(spend) / NULLIF(SUM(clicks), 0) AS cpc,
        SUM(spend) / NULLIF(SUM(conversions), 0) AS cpa,
        SUM(conversion_value) / NULLIF(SUM(spend), 0) AS roas
    FROM ads_reporting
    GROUP BY 1
    ORDER BY spend DESC
""").df())

print("\nTop campaigns by spend:\n")
print(con.execute("""
    SELECT
        platform,
        campaign_name,
        SUM(spend) AS spend,
        SUM(clicks) AS clicks,
        SUM(conversions) AS conversions
    FROM ads_reporting
    GROUP BY 1,2
    ORDER BY spend DESC
    LIMIT 10
""").df())

con.close()