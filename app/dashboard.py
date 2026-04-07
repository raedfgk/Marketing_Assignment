from __future__ import annotations

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


DB_PATH = "db/marketing.db"


st.set_page_config(
    page_title="Marketing Performance Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute(
        """
        SELECT *
        FROM ads_reporting
        ORDER BY date, platform, campaign_name
        """
    ).df()
    con.close()

    df["date"] = pd.to_datetime(df["date"])

    numeric_cols = [
        "spend",
        "impressions",
        "clicks",
        "conversions",
        "conversion_value",
        "video_views",
        "video_watch_25",
        "video_watch_50",
        "video_watch_75",
        "video_watch_100",
        "likes",
        "shares",
        "comments",
        "reach",
        "frequency",
        "quality_score",
        "search_impression_share",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def safe_div(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator is None:
        return None
    if pd.isna(numerator) or pd.isna(denominator):
        return None
    if denominator == 0:
        return None
    return float(numerator) / float(denominator)


def pretty_label(text: str | None) -> str:
    if text is None or pd.isna(text):
        return ""
    out = str(text).replace("_", " ").replace("-", " - ").strip()
    out = " ".join(out.split())
    return out

def is_currency_metric(metric_name: str) -> bool:
    return metric_name in {
        "spend",
        "conversion_value",
        "cpc",
        "cpm",
        "cpa",
        "cost_per_reach",
    }


def metric_display_name(metric_name: str) -> str:
    special = {
        "ctr": "CTR",
        "cpc": "CPC",
        "cpm": "CPM",
        "cpa": "CPA",
        "roas": "ROAS",
    }
    if metric_name in special:
        return special[metric_name]
    return pretty_label(metric_name).title()


def apply_chart_format(fig, metric_name: str, axis: str = "y") -> None:
    if metric_name in {"ctr", "conversion_rate", "spend_share", "conversion_share", "video_completion_rate",
                       "social_engagement_rate", "avg_search_impression_share", "weighted_search_impression_share"}:
        if axis == "y":
            fig.update_yaxes(tickformat=".0%")
        else:
            fig.update_xaxes(tickformat=".0%")
    elif metric_name == "roas":
        pass
    elif is_currency_metric(metric_name):
        if axis == "y":
            fig.update_yaxes(tickprefix="$", separatethousands=True)
        else:
            fig.update_xaxes(tickprefix="$", separatethousands=True)


def apply_chart_text_format(fig, metric_name: str) -> None:
    if metric_name in {"ctr", "conversion_rate", "spend_share", "conversion_share", "video_completion_rate",
                       "social_engagement_rate", "avg_search_impression_share", "weighted_search_impression_share"}:
        fig.update_traces(texttemplate="%{text:.1%}")
    elif metric_name == "roas":
        fig.update_traces(texttemplate="%{text:.2f}x")
    elif is_currency_metric(metric_name):
        fig.update_traces(texttemplate="$%{text:,.2f}")
    else:
        fig.update_traces(texttemplate="%{text:.2f}")

def title_platform(text: str | None) -> str:
    if text is None or pd.isna(text):
        return ""
    return str(text).title()


def fmt_currency(x: float | None, decimals: int = 2) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"${x:,.{decimals}f}"


def fmt_number(x: float | int | None, decimals: int = 0) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:,.{decimals}f}"


def fmt_pct(x: float | None, decimals: int = 2) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x * 100:,.{decimals}f}%"


def fmt_roas(x: float | None, decimals: int = 2) -> str:
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:,.{decimals}f}x"


def style_page() -> None:
    st.markdown(
        """
        <style>
        .hero-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 22px;
            border-radius: 18px;
            color: white;
            margin-bottom: 14px;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
            color: white;
        }
        .hero-subtitle {
            margin-top: 8px;
            margin-bottom: 0;
            font-size: 1rem;
            color: #e2e8f0;
        }
        .section-note {
            background-color: #f8fafc;
            border-left: 5px solid #334155;
            padding: 12px 14px;
            border-radius: 8px;
            margin: 6px 0 12px 0;
            color: #0f172a;
        }
        .kpi-card {
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 12px 14px;
            min-height: 88px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-bottom: 8px;
        }
        .kpi-label {
            font-size: 0.86rem;
            color: #475569;
            margin-bottom: 6px;
            font-weight: 600;
        }
        .kpi-value {
            font-size: 1.35rem;
            line-height: 1.2;
            color: #0f172a;
            font-weight: 700;
        }
        .small-note {
            color: #64748b;
            font-size: 0.85rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, tooltip: str) -> None:
    safe_tooltip = tooltip.replace('"', "&quot;")
    st.markdown(
        f"""
        <div class="kpi-card" title="{safe_tooltip}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def aggregate_metrics(df: pd.DataFrame) -> dict[str, float | None]:
    spend = df["spend"].sum()
    impressions = df["impressions"].sum()
    clicks = df["clicks"].sum()
    conversions = df["conversions"].sum()
    conversion_value = df["conversion_value"].sum(min_count=1)

    return {
        "spend": spend,
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "conversion_value": conversion_value,
        "ctr": safe_div(clicks, impressions),
        "cpc": safe_div(spend, clicks),
        "cpm": safe_div(spend * 1000, impressions),
        "cpa": safe_div(spend, conversions),
        "conversion_rate": safe_div(conversions, clicks),
        "roas": safe_div(conversion_value, spend),
    }


def platform_summary(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("platform", dropna=False, as_index=False)
        .agg(
            spend=("spend", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            conversion_value=("conversion_value", lambda s: s.sum(min_count=1)),
            video_views=("video_views", lambda s: s.sum(min_count=1)),
            video_watch_100=("video_watch_100", lambda s: s.sum(min_count=1)),
            likes=("likes", lambda s: s.sum(min_count=1)),
            shares=("shares", lambda s: s.sum(min_count=1)),
            comments=("comments", lambda s: s.sum(min_count=1)),
            reach=("reach", lambda s: s.sum(min_count=1)),
            frequency=("frequency", "mean"),
        )
        .copy()
    )

    total_spend = grouped["spend"].sum()
    total_conversions = grouped["conversions"].sum()

    grouped["ctr"] = grouped.apply(lambda r: safe_div(r["clicks"], r["impressions"]), axis=1)
    grouped["cpc"] = grouped.apply(lambda r: safe_div(r["spend"], r["clicks"]), axis=1)
    grouped["cpm"] = grouped.apply(lambda r: safe_div(r["spend"] * 1000, r["impressions"]), axis=1)
    grouped["cpa"] = grouped.apply(lambda r: safe_div(r["spend"], r["conversions"]), axis=1)
    grouped["conversion_rate"] = grouped.apply(lambda r: safe_div(r["conversions"], r["clicks"]), axis=1)
    grouped["roas"] = grouped.apply(lambda r: safe_div(r["conversion_value"], r["spend"]), axis=1)
    grouped["spend_share"] = grouped.apply(lambda r: safe_div(r["spend"], total_spend), axis=1)
    grouped["conversion_share"] = grouped.apply(lambda r: safe_div(r["conversions"], total_conversions), axis=1)
    grouped["efficiency_index"] = grouped.apply(
        lambda r: safe_div(r["conversion_share"], r["spend_share"]),
        axis=1,
    )

    engagements = grouped["likes"].fillna(0) + grouped["shares"].fillna(0) + grouped["comments"].fillna(0)
    grouped["social_engagement_rate"] = [
        safe_div(engagements.iloc[i], grouped["impressions"].iloc[i]) for i in range(len(grouped))
    ]
    grouped["video_completion_rate"] = [
        safe_div(grouped["video_watch_100"].iloc[i], grouped["video_views"].iloc[i]) for i in range(len(grouped))
    ]
    grouped["cost_per_reach"] = [
        safe_div(grouped["spend"].iloc[i], grouped["reach"].iloc[i]) for i in range(len(grouped))
    ]

    grouped["weighted_quality_score"] = pd.Series([None] * len(grouped), dtype="float64")
    grouped["weighted_search_impression_share"] = pd.Series([None] * len(grouped), dtype="float64")

    google_df = df[df["platform"] == "google"].copy()
    if not google_df.empty:
        google_impressions = google_df["impressions"].sum()

        weighted_quality_score = (
            (google_df["quality_score"] * google_df["impressions"]).sum() / google_impressions
            if google_df["quality_score"].notna().any() and google_impressions > 0
            else None
        )

        weighted_search_impression_share = (
            (google_df["search_impression_share"] * google_df["impressions"]).sum() / google_impressions
            if google_df["search_impression_share"].notna().any() and google_impressions > 0
            else None
        )

        grouped.loc[grouped["platform"] == "google", "weighted_quality_score"] = weighted_quality_score
        grouped.loc[
            grouped["platform"] == "google",
            "weighted_search_impression_share",
        ] = weighted_search_impression_share

    grouped["platform_display"] = grouped["platform"].map(title_platform)

    return grouped.sort_values("spend", ascending=False).reset_index(drop=True)


def daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("date", as_index=False)
        .agg(
            spend=("spend", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            conversion_value=("conversion_value", lambda s: s.sum(min_count=1)),
        )
        .copy()
    )

    grouped["ctr"] = grouped.apply(lambda r: safe_div(r["clicks"], r["impressions"]), axis=1)
    grouped["cpc"] = grouped.apply(lambda r: safe_div(r["spend"], r["clicks"]), axis=1)
    grouped["cpm"] = grouped.apply(lambda r: safe_div(r["spend"] * 1000, r["impressions"]), axis=1)
    grouped["cpa"] = grouped.apply(lambda r: safe_div(r["spend"], r["conversions"]), axis=1)
    grouped["conversion_rate"] = grouped.apply(lambda r: safe_div(r["conversions"], r["clicks"]), axis=1)
    grouped["roas"] = grouped.apply(lambda r: safe_div(r["conversion_value"], r["spend"]), axis=1)

    return grouped.sort_values("date").reset_index(drop=True)


def campaign_summary(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["platform", "campaign_name"], as_index=False)
        .agg(
            spend=("spend", "sum"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            conversions=("conversions", "sum"),
            conversion_value=("conversion_value", lambda s: s.sum(min_count=1)),
            video_views=("video_views", lambda s: s.sum(min_count=1)),
            video_watch_100=("video_watch_100", lambda s: s.sum(min_count=1)),
            likes=("likes", lambda s: s.sum(min_count=1)),
            shares=("shares", lambda s: s.sum(min_count=1)),
            comments=("comments", lambda s: s.sum(min_count=1)),
            reach=("reach", lambda s: s.sum(min_count=1)),
            avg_frequency=("frequency", "mean"),
            avg_quality_score=("quality_score", "mean"),
            avg_search_impression_share=("search_impression_share", "mean"),
        )
        .copy()
    )

    engagements = grouped["likes"].fillna(0) + grouped["shares"].fillna(0) + grouped["comments"].fillna(0)

    grouped["ctr"] = grouped.apply(lambda r: safe_div(r["clicks"], r["impressions"]), axis=1)
    grouped["cpc"] = grouped.apply(lambda r: safe_div(r["spend"], r["clicks"]), axis=1)
    grouped["cpm"] = grouped.apply(lambda r: safe_div(r["spend"] * 1000, r["impressions"]), axis=1)
    grouped["cpa"] = grouped.apply(lambda r: safe_div(r["spend"], r["conversions"]), axis=1)
    grouped["conversion_rate"] = grouped.apply(lambda r: safe_div(r["conversions"], r["clicks"]), axis=1)
    grouped["roas"] = grouped.apply(lambda r: safe_div(r["conversion_value"], r["spend"]), axis=1)
    grouped["video_completion_rate"] = [
        safe_div(grouped["video_watch_100"].iloc[i], grouped["video_views"].iloc[i]) for i in range(len(grouped))
    ]
    grouped["social_engagement_rate"] = [
        safe_div(engagements.iloc[i], grouped["impressions"].iloc[i]) for i in range(len(grouped))
    ]
    grouped["cost_per_reach"] = [
        safe_div(grouped["spend"].iloc[i], grouped["reach"].iloc[i]) for i in range(len(grouped))
    ]

    grouped["platform_display"] = grouped["platform"].map(title_platform)
    grouped["campaign_name_display"] = grouped["campaign_name"].map(pretty_label)
    grouped["campaign_label"] = grouped["platform_display"] + " | " + grouped["campaign_name_display"]

    return grouped.sort_values(["spend", "conversions"], ascending=[False, False]).reset_index(drop=True)


def data_coverage_table(df: pd.DataFrame) -> pd.DataFrame:
    coverage = pd.DataFrame(
        [
            {
                "Platform": "Facebook",
                "Revenue Tracking": "No",
                "Reach / Frequency": "Yes",
                "Video Depth Metrics": "Limited",
                "Social Engagement Metrics": "No",
                "Search Quality Metrics": "No",
            },
            {
                "Platform": "Google",
                "Revenue Tracking": "Yes",
                "Reach / Frequency": "No",
                "Video Depth Metrics": "No",
                "Social Engagement Metrics": "No",
                "Search Quality Metrics": "Yes",
            },
            {
                "Platform": "Tiktok",
                "Revenue Tracking": "No",
                "Reach / Frequency": "No",
                "Video Depth Metrics": "Yes",
                "Social Engagement Metrics": "Yes",
                "Search Quality Metrics": "No",
            },
        ]
    )

    selected_platforms = [title_platform(x) for x in sorted(df["platform"].dropna().unique())]
    return coverage[coverage["Platform"].isin(selected_platforms)].copy()


def build_takeaways(platform_df: pd.DataFrame) -> list[str]:
    if platform_df.empty:
        return []

    out: list[str] = []

    spend_leader = platform_df.sort_values("spend", ascending=False).iloc[0]
    out.append(
        f"{spend_leader['platform_display']} is the largest budget recipient at "
        f"{fmt_currency(spend_leader['spend'], 1)} ({fmt_pct(spend_leader['spend_share'])} of spend)."
    )

    best_cpa_df = platform_df.dropna(subset=["cpa"])
    if not best_cpa_df.empty:
        best_cpa = best_cpa_df.sort_values("cpa").iloc[0]
        out.append(
            f"{best_cpa['platform_display']} has the lowest Cost Per Acquisition at "
            f"{fmt_currency(best_cpa['cpa'], 2)}."
        )

    best_eff_df = platform_df.dropna(subset=["efficiency_index"])
    if not best_eff_df.empty:
        best_eff = best_eff_df.sort_values("efficiency_index", ascending=False).iloc[0]
        out.append(
            f"{best_eff['platform_display']} has the strongest spend-to-conversion efficiency index at "
            f"{best_eff['efficiency_index']:.2f}."
        )

    roas_df = platform_df.dropna(subset=["roas"])
    if not roas_df.empty:
        best_roas = roas_df.sort_values("roas", ascending=False).iloc[0]
        out.append(
            f"{best_roas['platform_display']} leads tracked Return on Ad Spend at "
            f"{fmt_roas(best_roas['roas'])}."
        )
    else:
        out.append("Return on Ad Spend is only available where conversion value is tracked.")

    return out


def recommendations(platform_df: pd.DataFrame) -> list[str]:
    recs: list[str] = []
    if platform_df.empty:
        return recs

    spend_heavy = platform_df.sort_values("spend_share", ascending=False).iloc[0]
    recs.append(
        f"Review budget concentration in {spend_heavy['platform_display']}, since it carries the largest share of spend."
    )

    cpa_best_df = platform_df.dropna(subset=["cpa"])
    if not cpa_best_df.empty:
        cpa_best = cpa_best_df.sort_values("cpa").iloc[0]
        recs.append(
            f"Consider scaling the strongest efficiency channel, currently {cpa_best['platform_display']}, based on Cost Per Acquisition."
        )

    roas_df = platform_df.dropna(subset=["roas"])
    if not roas_df.empty:
        roas_best = roas_df.sort_values("roas", ascending=False).iloc[0]
        recs.append(
            f"Protect or expand budget in {roas_best['platform_display']} where tracked revenue supports strong return."
        )

    if "tiktok" in platform_df["platform"].tolist():
        recs.append(
            "Improve TikTok revenue attribution so ROI can be compared consistently across all channels."
        )

    return recs


def format_platform_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    rename_map = {
        "platform_display": "Platform",
        "spend": "Spend",
        "spend_share": "Spend Share",
        "conversions": "Conversions",
        "conversion_share": "Conversion Share",
        "ctr": "CTR",
        "conversion_rate": "Conversion Rate",
        "cpa": "CPA",
        "roas": "ROAS",
        "efficiency_index": "Efficiency Index",
        "video_completion_rate": "Video Completion Rate",
        "social_engagement_rate": "Social Engagement Rate",
        "cost_per_reach": "Cost Per Reach",
        "weighted_quality_score": "Weighted Quality Score",
        "weighted_search_impression_share": "Weighted Search Impression Share",
    }
    out = out.rename(columns=rename_map)

    currency_cols = {"Spend", "CPA", "Cost Per Reach"}
    pct_cols = {
        "Spend Share",
        "Conversion Share",
        "CTR",
        "Conversion Rate",
        "Video Completion Rate",
        "Social Engagement Rate",
        "Weighted Search Impression Share",
    }

    for col in currency_cols:
        if col in out.columns:
            out[col] = out[col].map(lambda x: fmt_currency(x, 2))
    for col in pct_cols:
        if col in out.columns:
            out[col] = out[col].map(lambda x: fmt_pct(x, 2))
    if "ROAS" in out.columns:
        out["ROAS"] = out["ROAS"].map(lambda x: fmt_roas(x, 2))
    if "Efficiency Index" in out.columns:
        out["Efficiency Index"] = out["Efficiency Index"].map(
            lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A"
        )
    if "Weighted Quality Score" in out.columns:
        out["Weighted Quality Score"] = out["Weighted Quality Score"].map(
            lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A"
        )
    if "Conversions" in out.columns:
        out["Conversions"] = out["Conversions"].map(lambda x: fmt_number(x, 0))

    return out

def format_campaign_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    rename_map = {
        "platform_display": "Platform",
        "campaign_name_display": "Campaign",
        "spend": "Spend",
        "impressions": "Impressions",
        "clicks": "Clicks",
        "conversions": "Conversions",
        "ctr": "CTR",
        "conversion_rate": "Conversion Rate",
        "cpm": "CPM",
        "cpc": "CPC",
        "cpa": "CPA",
        "roas": "ROAS",
        "conversion_value": "Tracked Revenue",
        "video_completion_rate": "Video Completion Rate",
        "social_engagement_rate": "Social Engagement Rate",
        "cost_per_reach": "Cost Per Reach",
        "avg_quality_score": "Avg Quality Score",
        "avg_search_impression_share": "Avg Search Impression Share",
        "avg_frequency": "Avg Frequency",
    }
    out = out.rename(columns=rename_map)

    currency_cols = {"Spend", "Tracked Revenue", "CPM", "CPC", "CPA", "Cost Per Reach"}
    pct_cols = {
        "CTR",
        "Conversion Rate",
        "Video Completion Rate",
        "Social Engagement Rate",
        "Avg Search Impression Share",
    }
    number_cols = {"Impressions", "Clicks", "Conversions"}
    plain_decimal_cols = {"Avg Quality Score", "Avg Frequency"}

    for col in currency_cols:
        if col in out.columns:
            decimals = 3 if col == "CPC" else 2
            out[col] = out[col].map(lambda x, d=decimals: fmt_currency(x, d))
    for col in pct_cols:
        if col in out.columns:
            out[col] = out[col].map(lambda x: fmt_pct(x, 2))
    for col in number_cols:
        if col in out.columns:
            out[col] = out[col].map(lambda x: fmt_number(x, 0))
    for col in plain_decimal_cols:
        if col in out.columns:
            out[col] = out[col].map(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
    if "ROAS" in out.columns:
        out["ROAS"] = out["ROAS"].map(lambda x: fmt_roas(x, 2))

    return out


style_page()
df = load_data()

st.markdown(
    """
    <div class="hero-box">
        <p class="hero-title">Marketing Performance Dashboard</p>
        <p class="hero-subtitle">
            Integrated marketing performance dashboard for cross-channel analysis of Facebook, Google Ads, and TikTok campaign outcomes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Filters")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    all_platforms = sorted(df["platform"].dropna().unique().tolist())
    selected_platforms = st.multiselect(
        "Platform",
        options=all_platforms,
        default=all_platforms,
        format_func=title_platform,
    )

    campaign_options = sorted(df["campaign_name"].dropna().unique().tolist())
    selected_campaigns = st.multiselect(
        "Campaign",
        options=campaign_options,
        default=campaign_options,
        format_func=pretty_label,
    )

    ad_group_options = sorted(df["ad_group_name"].dropna().unique().tolist())
    selected_ad_groups = st.multiselect(
        "Ad Group",
        options=ad_group_options,
        default=ad_group_options,
        format_func=pretty_label,
    )

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = df["date"].min()
    end_date = df["date"].max()

filtered_df = df[
    (df["date"] >= start_date)
    & (df["date"] <= end_date)
    & (df["platform"].isin(selected_platforms))
    & (df["campaign_name"].isin(selected_campaigns))
    & (df["ad_group_name"].isin(selected_ad_groups))
].copy()

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

metrics = aggregate_metrics(filtered_df)
platform_df = platform_summary(filtered_df)
daily_df = daily_summary(filtered_df)
campaign_df = campaign_summary(filtered_df)
coverage_df = data_coverage_table(filtered_df)

st.markdown(
    f"""
    <div class="section-note">
        Reporting period: <strong>{start_date.date()}</strong> to <strong>{end_date.date()}</strong> |
        Platforms selected: <strong>{len(selected_platforms)}</strong> |
        Campaigns selected: <strong>{len(selected_campaigns)}</strong> |
        Ad groups selected: <strong>{len(selected_ad_groups)}</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Executive Summary")
st.caption("Hover over any metric card to see its meaning and interpretation.")

row1 = st.columns(5)
with row1[0]:
    render_kpi_card(
        "Total Spend",
        fmt_currency(metrics["spend"], 1),
        "Total Spend = total advertising cost across the selected filters. This shows how much budget was deployed."
    )
with row1[1]:
    render_kpi_card(
        "Impressions",
        fmt_number(metrics["impressions"], 0),
        "Impressions = total number of times ads were shown to users. This measures delivery scale, not unique people reached."
    )
with row1[2]:
    render_kpi_card(
        "Clicks",
        fmt_number(metrics["clicks"], 0),
        "Clicks = total number of ad clicks. This measures traffic generated by the selected campaigns."
    )
with row1[3]:
    render_kpi_card(
        "Conversions",
        fmt_number(metrics["conversions"], 0),
        "Conversions = total number of desired actions completed after ad interaction, such as sign-ups or purchases."
    )
with row1[4]:
    render_kpi_card(
        "Tracked Revenue",
        fmt_currency(metrics["conversion_value"], 1),
        "Tracked Revenue = revenue attributed to conversions where conversion value is available in the source data."
    )

row2 = st.columns(5)
with row2[0]:
    render_kpi_card(
        "Click-Through Rate",
        fmt_pct(metrics["ctr"]),
        "Click-Through Rate = clicks divided by impressions. It shows how often people clicked after seeing the ad."
    )
with row2[1]:
    render_kpi_card(
        "Cost Per Click",
        fmt_currency(metrics["cpc"], 3),
        "Cost Per Click = spend divided by clicks. Lower values mean traffic is being acquired more cheaply."
    )
with row2[2]:
    render_kpi_card(
        "Cost Per Mille",
        fmt_currency(metrics["cpm"], 2),
        "Cost Per Click = spend divided by clicks. Lower values mean traffic is being acquired more cheaply."
    )
with row2[3]:
    render_kpi_card(
        "Cost Per Acquisition",
        fmt_currency(metrics["cpa"], 2),
        "Cost Per Acquisition = spend divided by conversions. Lower CPA means conversions are being generated more efficiently."
    )
with row2[4]:
    render_kpi_card(
        "Conversion Rate",
        fmt_pct(metrics["conversion_rate"]),
        "Conversion Rate = conversions divided by clicks. This measures how effectively traffic turns into outcomes after the click."
    )

row3 = st.columns([1, 1, 1, 1, 1])
with row3[0]:
    render_kpi_card(
        "Return on Ad Spend",
        fmt_roas(metrics["roas"]),
        "Return on Ad Spend = tracked revenue divided by spend. Higher ROAS indicates stronger tracked financial return."
    )
with row3[4]:
    render_kpi_card(
        "Rows in Scope",
        fmt_number(len(filtered_df), 0),
        "Rows in Scope = number of records included after the current filters are applied."

    )

st.divider()

left, right = st.columns([1.2, 1.0])

with left:
    st.subheader("Key Takeaways")
    for item in build_takeaways(platform_df):
        st.markdown(f"- {item}")

with right:
    st.subheader("Recommendations")
    for item in recommendations(platform_df):
        st.markdown(f"- {item}")

st.divider()

tab_overview, tab_campaigns, tab_diagnostics, tab_coverage = st.tabs(
    ["Channel Overview", "Campaign Deep Dive", "Platform Diagnostics", "Data Coverage"]
)

with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Spend vs Conversion Share by Platform**")
        spend_conv_df = platform_df[["platform_display", "spend_share", "conversion_share"]].copy()
        spend_conv_long = spend_conv_df.melt(
            id_vars="platform_display",
            value_vars=["spend_share", "conversion_share"],
            var_name="metric",
            value_name="value",
        )
        spend_conv_long["metric"] = spend_conv_long["metric"].replace(
            {"spend_share": "Spend Share", "conversion_share": "Conversion Share"}
        )

        fig_share = px.bar(
            spend_conv_long,
            x="platform_display",
            y="value",
            color="metric",
            barmode="group",
            text="value",
        )
        fig_share.update_traces(texttemplate="%{text:.1%}")
        fig_share.update_layout(
            xaxis_title="Platform",
            yaxis_title="Share",
            yaxis_tickformat=".0%",
            legend_title="Metric",
            margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(
            fig_share,
            config={"displayModeBar": False},
            key="fig_share_platform_mix",
        )

    with c2:
        st.markdown("**Efficiency Comparison**")
        metric_choice = st.selectbox(
            "Platform comparison metric",
            options=["cpa", "ctr", "cpc", "conversion_rate", "roas", "efficiency_index"],
            index=0,
            key="platform_metric_choice",
            format_func=lambda x: pretty_label(x.upper() if x in {"ctr", "cpc", "cpa", "roas"} else x),
        )

        fig_platform = px.bar(
            platform_df.sort_values(metric_choice, ascending=(metric_choice in {"cpa", "cpc"})),
            x="platform_display",
            y=metric_choice,
            text=metric_choice,
        )
        apply_chart_format(fig_platform, metric_choice, axis="y")
        apply_chart_text_format(fig_platform, metric_choice)

        fig_platform.update_layout(
            xaxis_title="Platform",
            yaxis_title=metric_display_name(metric_choice),
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
        )
        st.plotly_chart(
            fig_platform,
            config={"displayModeBar": False},
            key="fig_platform_comparison",
        )

    st.markdown("**Platform Summary Table**")
    platform_table = format_platform_table(
        platform_df[
            [
                "platform_display",
                "spend",
                "spend_share",
                "conversions",
                "conversion_share",
                "ctr",
                "conversion_rate",
                "cpa",
                "roas",
                "efficiency_index",
            ]
        ]
    )
    st.dataframe(platform_table, hide_index=True, width="stretch")

    st.markdown("**Daily Trend**")
    trend_metric = st.selectbox(
        "Trend metric",
        options=["spend", "clicks", "conversions", "ctr", "conversion_rate", "cpa", "roas"],
        index=0,
        key="daily_trend_metric",
        format_func=lambda x: pretty_label(x.upper() if x in {"ctr", "cpa", "roas"} else x).title(),
    )

    fig_trend = px.line(
        daily_df,
        x="date",
        y=trend_metric,
        markers=True,
    )
    apply_chart_format(fig_trend, trend_metric, axis="y")
    fig_trend.update_layout(
        xaxis_title="Date",
        yaxis_title=metric_display_name(trend_metric),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(
        fig_trend,
        config={"displayModeBar": False},
        key="fig_daily_trend",
    )

with tab_campaigns:
    top_n = st.slider("Campaign rows", min_value=5, max_value=20, value=10)

    sort_metric = st.selectbox(
        "Sort campaigns by",
        options=["spend", "conversions", "ctr", "cpc", "cpm", "cpa", "conversion_rate", "roas"],
        index=0,
        key="campaign_sort_metric",
        format_func=lambda x: pretty_label(x.upper() if x in {"ctr", "cpc", "cpm", "cpa", "roas"} else x).title(),
    )

    ascending = sort_metric in {"cpc", "cpm", "cpa"}
    campaign_view = campaign_df.sort_values(sort_metric, ascending=ascending).head(top_n).copy()

    st.markdown("**Top Campaigns**")
    fig_campaign = px.bar(
        campaign_view,
        x=sort_metric,
        y="campaign_label",
        color="platform_display",
        orientation="h",
        text=sort_metric,
    )
    apply_chart_format(fig_campaign, sort_metric, axis="x")
    apply_chart_text_format(fig_campaign, sort_metric)

    fig_campaign.update_layout(
        xaxis_title=metric_display_name(sort_metric),
        yaxis_title="Campaign",
        legend_title="Platform",
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(
        fig_campaign,
        config={"displayModeBar": False},
        key="fig_campaign_ranking",
    )

    st.markdown("**Campaign Detail Table**")
    campaign_table = format_campaign_table(
        campaign_view[
            [
                "platform_display",
                "campaign_name_display",
                "spend",
                "impressions",
                "clicks",
                "conversions",
                "ctr",
                "conversion_rate",
                "cpa",
                "roas",
            ]
        ]
    )
    st.dataframe(campaign_table, hide_index=True, width="stretch")

with tab_diagnostics:
    d1, d2 = st.columns(2)

    google_df = campaign_df[campaign_df["platform"] == "google"].copy()
    social_df = campaign_df[campaign_df["platform"].isin(["facebook", "tiktok"])].copy()

    with d1:
        st.markdown("**Google Diagnostics**")
        if google_df.empty:
            st.info("No Google data in the current filter selection.")
        else:
            google_metric = st.selectbox(
                "Google metric",
                options=["avg_quality_score", "avg_search_impression_share", "roas", "conversion_rate", "cpa"],
                index=0,
                key="google_diag_metric",
                format_func=lambda x: pretty_label(x.upper() if x in {"cpa", "roas"} else x).title(),
            )

            google_metric_df = google_df.dropna(subset=[google_metric]).copy()

            if google_metric_df.empty:
                st.info("The selected metric is not available for the current Google filter set.")
            else:
                fig_google = px.bar(
                    google_metric_df.sort_values(google_metric, ascending=(google_metric == "cpa")),
                    x="campaign_name_display",
                    y=google_metric,
                    text=google_metric,
                )
                apply_chart_format(fig_google, google_metric, axis="y")
                apply_chart_text_format(fig_google, google_metric)

                fig_google.update_layout(
                    xaxis_title="Google Campaign",
                    yaxis_title=metric_display_name(google_metric),
                    margin=dict(l=10, r=10, t=30, b=10),
                )
                st.plotly_chart(
                    fig_google,
                    config={"displayModeBar": False},
                    key="fig_google_diagnostics",
                )

                google_table = format_campaign_table(
                    google_metric_df[
                        [
                            "platform_display",
                            "campaign_name_display",
                            "spend",
                            "conversions",
                            "roas",
                            "avg_quality_score",
                            "avg_search_impression_share",
                        ]
                    ]
                )
                st.dataframe(google_table, hide_index=True, width="stretch")

    with d2:
        st.markdown("**Social and Video Diagnostics (platform-specific metrics only)**")
        if social_df.empty:
            st.info("No Facebook or TikTok data in the current filter selection.")
        else:
            social_metric = st.selectbox(
                "Social metric",
                options=["video_completion_rate", "social_engagement_rate", "cost_per_reach", "ctr", "conversion_rate"],
                index=0,
                key="social_diag_metric",
                format_func=lambda x: pretty_label(x.upper() if x in {"ctr"} else x).title(),
            )

            social_metric_df = social_df[social_df[social_metric].notna()].copy()

            if social_metric == "video_completion_rate":
                social_metric_df = social_metric_df[social_metric_df["video_views"].fillna(0) > 0].copy()

            if social_metric == "social_engagement_rate":
                social_metric_df = social_metric_df[
                    (
                        social_metric_df["likes"].fillna(0)
                        + social_metric_df["shares"].fillna(0)
                        + social_metric_df["comments"].fillna(0)
                    ) > 0
                ].copy()

            if social_metric == "cost_per_reach":
                social_metric_df = social_metric_df[social_metric_df["reach"].fillna(0) > 0].copy()

            if social_metric_df.empty:
                st.info("The selected metric is not available for the current social-platform filter set.")
            else:
                fig_social = px.bar(
                    social_metric_df.sort_values(social_metric, ascending=(social_metric == "cost_per_reach")),
                    x="campaign_name_display",
                    y=social_metric,
                    color="platform_display",
                    text=social_metric,
                )

                apply_chart_format(fig_social, social_metric, axis="y")
                apply_chart_text_format(fig_social, social_metric)

                fig_social.update_layout(
                    xaxis_title="Campaign",
                    yaxis_title=metric_display_name(social_metric),
                    legend_title="Platform",
                    margin=dict(l=10, r=10, t=30, b=10),
                )
                st.plotly_chart(
                    fig_social,
                    config={"displayModeBar": False},
                    key="fig_social_diagnostics",
                )

                social_table = format_campaign_table(
                    social_metric_df[
                        [
                            "platform_display",
                            "campaign_name_display",
                            "video_completion_rate",
                            "social_engagement_rate",
                            "cost_per_reach",
                            "ctr",
                            "conversion_rate",
                        ]
                    ]
                )
                st.dataframe(social_table, hide_index=True, width="stretch")

with tab_coverage:
    st.markdown(
        """
        **Metric availability matters.**  
        Some KPIs are directly comparable across all channels, while others only exist for specific platforms.
        """
    )
    st.dataframe(coverage_df, hide_index=True, width="stretch")

    st.markdown(
        """
        **Model Notes**
        - `ads_unified` is the standardized cross-platform base table.
        - `ads_reporting` is the analytics-ready layer with derived KPIs such as CTR, CPC, CPM, CPA, Conversion Rate, and ROAS.
        - Revenue-based ROI is only measurable where `conversion_value` exists.
        - Platform-specific diagnostics are preserved instead of being discarded during unification.
        """
    )