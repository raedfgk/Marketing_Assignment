import duckdb

DB_PATH = "db/marketing.db"


def main() -> None:
    con = duckdb.connect(DB_PATH)

    checks = {
        "null_dates": """
            SELECT COUNT(*) AS n
            FROM ads_unified
            WHERE date IS NULL
        """,
        "negative_spend": """
            SELECT COUNT(*) AS n
            FROM ads_unified
            WHERE spend < 0
        """,
        "negative_clicks": """
            SELECT COUNT(*) AS n
            FROM ads_unified
            WHERE clicks < 0
        """,
        "clicks_gt_impressions": """
            SELECT COUNT(*) AS n
            FROM ads_unified
            WHERE clicks > impressions
        """,
        "conversions_gt_clicks": """
            SELECT COUNT(*) AS n
            FROM ads_unified
            WHERE conversions > clicks
        """,
        "duplicate_grain": """
            SELECT COUNT(*) AS n
            FROM (
                SELECT
                    date, platform, campaign_id, ad_group_id,
                    COUNT(*) AS row_count
                FROM ads_unified
                GROUP BY 1,2,3,4
                HAVING COUNT(*) > 1
            )
        """
    }

    failed = False

    for name, query in checks.items():
        n = con.execute(query).fetchone()[0]
        print(f"{name}: {n}")
        if n != 0:
            failed = True

    con.close()

    if failed:
        raise ValueError("One or more QA checks failed.")

    print("All QA checks passed.")


if __name__ == "__main__":
    main()