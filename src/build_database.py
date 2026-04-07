from pathlib import Path
import duckdb

DB_PATH = "db/marketing.db"
DATA_DIR = Path("data")


def main() -> None:
    Path("db").mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(DB_PATH)

    # Raw tables
    con.execute("""
        CREATE OR REPLACE TABLE raw_facebook_ads AS
        SELECT *
        FROM read_csv_auto('data/01_facebook_ads.csv', header=True);
    """)

    con.execute("""
        CREATE OR REPLACE TABLE raw_google_ads AS
        SELECT *
        FROM read_csv_auto('data/02_google_ads.csv', header=True);
    """)

    con.execute("""
        CREATE OR REPLACE TABLE raw_tiktok_ads AS
        SELECT *
        FROM read_csv_auto('data/03_tiktok_ads.csv', header=True);
    """)

    # Unified table
    con.execute("""
        CREATE OR REPLACE TABLE ads_unified AS

        SELECT
            CAST(date AS DATE) AS date,
            'facebook' AS platform,
            campaign_id,
            campaign_name,
            ad_set_id AS ad_group_id,
            ad_set_name AS ad_group_name,
            impressions,
            clicks,
            spend,
            conversions,
            NULL::DOUBLE AS conversion_value,
            video_views,
            NULL::BIGINT AS video_watch_25,
            NULL::BIGINT AS video_watch_50,
            NULL::BIGINT AS video_watch_75,
            NULL::BIGINT AS video_watch_100,
            NULL::BIGINT AS likes,
            NULL::BIGINT AS shares,
            NULL::BIGINT AS comments,
            engagement_rate,
            reach,
            frequency,
            NULL::DOUBLE AS ctr_source,
            NULL::DOUBLE AS avg_cpc_source,
            NULL::INTEGER AS quality_score,
            NULL::DOUBLE AS search_impression_share
        FROM raw_facebook_ads

        UNION ALL

        SELECT
            CAST(date AS DATE) AS date,
            'google' AS platform,
            campaign_id,
            campaign_name,
            ad_group_id,
            ad_group_name,
            impressions,
            clicks,
            cost AS spend,
            conversions,
            conversion_value,
            NULL::BIGINT AS video_views,
            NULL::BIGINT AS video_watch_25,
            NULL::BIGINT AS video_watch_50,
            NULL::BIGINT AS video_watch_75,
            NULL::BIGINT AS video_watch_100,
            NULL::BIGINT AS likes,
            NULL::BIGINT AS shares,
            NULL::BIGINT AS comments,
            NULL::DOUBLE AS engagement_rate,
            NULL::BIGINT AS reach,
            NULL::DOUBLE AS frequency,
            ctr AS ctr_source,
            avg_cpc AS avg_cpc_source,
            quality_score,
            search_impression_share
        FROM raw_google_ads

        UNION ALL

        SELECT
            CAST(date AS DATE) AS date,
            'tiktok' AS platform,
            campaign_id,
            campaign_name,
            adgroup_id AS ad_group_id,
            adgroup_name AS ad_group_name,
            impressions,
            clicks,
            cost AS spend,
            conversions,
            NULL::DOUBLE AS conversion_value,
            video_views,
            video_watch_25,
            video_watch_50,
            video_watch_75,
            video_watch_100,
            likes,
            shares,
            comments,
            NULL::DOUBLE AS engagement_rate,
            NULL::BIGINT AS reach,
            NULL::DOUBLE AS frequency,
            NULL::DOUBLE AS ctr_source,
            NULL::DOUBLE AS avg_cpc_source,
            NULL::INTEGER AS quality_score,
            NULL::DOUBLE AS search_impression_share
        FROM raw_tiktok_ads
    """)

    # Reporting table with derived KPIs
    con.execute("""
        CREATE OR REPLACE TABLE ads_reporting AS
        SELECT
            *,

            -- Core metrics
            CASE WHEN impressions = 0 THEN NULL ELSE clicks::DOUBLE / impressions END AS ctr,
            CASE WHEN clicks = 0 THEN NULL ELSE spend / clicks END AS cpc,
            CASE WHEN impressions = 0 THEN NULL ELSE spend * 1000.0 / impressions END AS cpm,
            CASE WHEN conversions = 0 THEN NULL ELSE spend / conversions END AS cpa,
            CASE WHEN clicks = 0 THEN NULL ELSE conversions::DOUBLE / clicks END AS conversion_rate,
            CASE WHEN spend = 0 THEN NULL ELSE conversion_value / spend END AS roas,

            -- Social / video metrics
            CASE WHEN video_views = 0 THEN NULL ELSE video_watch_100::DOUBLE / video_views END AS video_completion_rate,
            CASE WHEN impressions = 0 THEN NULL ELSE (likes + shares + comments)::DOUBLE / impressions END AS social_engagement_rate,

            -- Facebook-specific efficiency
            CASE WHEN reach = 0 THEN NULL ELSE spend / reach END AS cost_per_reach

        FROM ads_unified;
    """)

    Path("data").mkdir(parents=True, exist_ok=True)

    con.execute("""
        COPY ads_unified TO 'data/ads_unified.csv' (HEADER, DELIMITER ',');
    """)

    con.execute("""
        COPY ads_reporting TO 'data/ads_reporting.csv' (HEADER, DELIMITER ',');
    """)

    con.close()
    print(f"DuckDB database built at: {DB_PATH}")


if __name__ == "__main__":
    main()