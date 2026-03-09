"""
Charts — Cumulative production charts with Plotly.
Side-by-side layout, gradient fills, per-point colored labels, clean design.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import OP_HOURS, COLORS
from calculations.formatting import fmt


# ── Color palette ─────────────────────────────────────────────
CHART_COLORS = {
    "ob": {"line": "#f59e0b", "fill": "rgba(245,158,11,0.10)", "marker": "#d97706"},
    "ch": {"line": "#3b82f6", "fill": "rgba(59,130,246,0.10)", "marker": "#2563eb"},
    "plan": "#94a3b8",
    "target": "#e2e8f0",
    "success": "#10b981",
    "danger": "#f43f5e",
}


def build_cumm_chart(
    actual_df,
    value_col: str,
    plan_cumm_col: str,
    plan_daily_val: float,
    title: str,
    y_label: str,
    cumm_pit: pd.DataFrame,
    convert_kg: bool = False,
    palette: str = "ob",
) -> go.Figure:
    """Build cumulative chart with gradient fill and per-point labels."""

    colors = CHART_COLORS[palette]

    # --- Actual: group by Hour LU ---
    hourly = actual_df.groupby("Hour LU")[value_col].sum().reset_index()
    hourly.columns = ["Hour", "Actual"]
    if convert_kg:
        hourly["Actual"] = hourly["Actual"] / 1000

    hourly_full = pd.DataFrame({"Hour": OP_HOURS})
    hourly_full = hourly_full.merge(hourly, on="Hour", how="left").fillna(0)
    hourly_full["Cumm_Actual"] = hourly_full["Actual"].cumsum()

    # --- Plan cumulative curve ---
    plan_full = pd.DataFrame({"Hour": OP_HOURS})
    if len(cumm_pit) > 0:
        plan_data = cumm_pit[["Hour LU", plan_cumm_col]].rename(columns={"Hour LU": "Hour"})
        plan_full = plan_full.merge(plan_data, on="Hour", how="left")
        plan_full[plan_cumm_col] = plan_full[plan_cumm_col].ffill().fillna(0)
    else:
        plan_full[plan_cumm_col] = 0

    # Last hour with data
    has_data = hourly_full[hourly_full["Actual"] > 0]
    last_actual_idx = has_data.index.max() if len(has_data) > 0 else -1

    fig = go.Figure()

    # 1) Plan daily target (horizontal dashed line)
    if plan_daily_val > 0:
        fig.add_hline(
            y=plan_daily_val,
            line_dash="dash",
            line_color=colors["line"],
            line_width=1.5,
            annotation_text=f"<b>Plan: {fmt(plan_daily_val)}</b>",
            annotation_position="top left",
            annotation_font=dict(size=12, color=colors["line"]),
        )

    # 2) Actual area fill + line
    if last_actual_idx >= 0:
        show = hourly_full.iloc[: last_actual_idx + 1].copy()
        total_actual = show["Cumm_Actual"].iloc[-1]
        hours_count = len(show[show["Actual"] > 0])
        avg_per_hour = total_actual / hours_count if hours_count > 0 else 0

        # Create custom hover text for each data point
        hover_texts = []
        for v, h in zip(show["Cumm_Actual"], show["Hour"]):
            if v >= 1000:
                hover_texts.append(f"{v/1000:.1f}k at {h}")
            else:
                hover_texts.append(f"{v:,.0f} at {h}")

        # Gradient area fill
        fig.add_trace(
            go.Scatter(
                x=show["Hour"],
                y=show["Cumm_Actual"],
                mode="none",
                fill="tozeroy",
                fillcolor=colors["fill"],
                showlegend=False,
                hoverinfo="skip",
            )
        )

        # Main line with colored markers (neutral theme color for history)
        marker_colors = [colors["marker"]] * len(show)

        # Generate text labels and their dynamic colors (green above target, red below)
        text_labels = [f"<b>{v/1000:.1f}K</b>" for v in show["Cumm_Actual"]]
        text_colors = [
            CHART_COLORS["success"] if v >= plan_daily_val else CHART_COLORS["danger"]
            for v in show["Cumm_Actual"]
        ]

        # Use numerical X-coordinates mapped to OP_HOURS index so we can plot precise fractional intersections
        x_coords = [OP_HOURS.index(h) for h in show["Hour"]]

        fig.add_trace(
            go.Scatter(
                x=x_coords,
                y=show["Cumm_Actual"],
                customdata=hover_texts,
                mode="lines+markers+text",
                name="Actual",
                text=text_labels,
                textposition="top center",
                textfont=dict(size=9, color=text_colors, family="Inter"),
                line=dict(color=colors["line"], width=2.5, shape="spline"),
                marker=dict(
                    size=7, color=marker_colors,
                    line=dict(color="#fff", width=1.5),
                ),
                hovertemplate="Actual<br><b>%{customdata}</b><extra></extra>",
            )
        )

        # Last point highlight
        last = show.iloc[-1]
        is_above = last["Cumm_Actual"] >= plan_daily_val
        dot_color = CHART_COLORS["success"] if is_above else CHART_COLORS["danger"]

        fig.add_trace(
            go.Scatter(
                x=[x_coords[-1]],
                y=[last["Cumm_Actual"]],
                mode="markers",
                marker=dict(size=12, color=dot_color, line=dict(color="#fff", width=2)),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        # Vertical dashed line at the exact HOUR point where it first hits/crosses the target
        intersect_x = None
        y_vals = show["Cumm_Actual"].tolist()
        for i in range(len(y_vals)):
            if y_vals[i] >= plan_daily_val:
                intersect_x = OP_HOURS.index(show.iloc[i]["Hour"])
                break

        if intersect_x is not None:
            fig.add_shape(
                type="line",
                x0=intersect_x,
                x1=intersect_x,
                y0=0,
                y1=plan_daily_val, # Touches exactly the target line
                line=dict(color=CHART_COLORS["success"], width=1.5, dash="dash"),
                layer="above" 
            )
        
        # (Manual data point annotations removed in favor of native scatter textposition)
        # Summary annotation (above chart, right side)
        summary_text = (
            f"<span style='font-size:14px;color:{colors['marker']}'><b>{fmt(total_actual / 1000, 1)}K</b></span>  "
            f"<span style='font-size:13px;color:#64748b;font-weight:600;'>Avg {fmt(avg_per_hour / 1000, 1)}K/hr · {hours_count}h</span>"
        )
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.98, y=1.12,  # Give a safe distance from mode icons
            text=summary_text,
            showarrow=False,
            font=dict(family="Inter"),
            align="right",
            xanchor="right",
        )

    # Dynamic Y-axis range
    all_y = []
    if last_actual_idx >= 0:
        all_y.append(hourly_full.iloc[:last_actual_idx + 1]["Cumm_Actual"].max())
    if plan_daily_val > 0:
        all_y.append(plan_daily_val)
    # Revert multiplier to normal spacing (1.10) to avoid excessive gap at the top
    y_max = max(all_y) * 1.10 if all_y else 100

    # Layout
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=14, family="Inter", color="#1a1f36"),
            x=0.01, y=0.97,
        ),
        height=420,  # Increased height
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(OP_HOURS))),
            ticktext=OP_HOURS,
            range=[-0.5, len(OP_HOURS) - 0.5], # Ensure full 24-hours is visible
            showgrid=False,
            linecolor="#e5e7eb",
            linewidth=1,
            tickfont=dict(size=11, color="#475569", family="Inter"),
            tickangle=0,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f3f4f6",
            gridwidth=1,
            zeroline=False,
            showline=False,
            tickfont=dict(size=9, color="#9ca3af", family="Inter"),
            range=[0, y_max],
        ),
        legend=dict(
            orientation="h", y=-0.15,
            font=dict(size=10, color="#6b7280", family="Inter"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=50, b=40, r=16, l=40),
        font=dict(family="Inter"),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font=dict(color="#111827", size=12, family="Inter"),
            bordercolor="#e5e7eb",
        ),
    )
    return fig


def render_production_charts(
    ob_f, ch_f, cumm_pit, plan_ob_val: float, plan_ch_val: float
):
    """Render OB and CH cumulative charts side-by-side."""
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    col_ob, col_ch = st.columns(2, gap="small")

    with col_ob:
        fig_ob = build_cumm_chart(
            ob_f, "Volume", "Cumm OB", plan_ob_val,
            "Cumulative OB Production", "BCM",
            cumm_pit, palette="ob",
        )
        st.plotly_chart(fig_ob, width="stretch")

    with col_ch:
        fig_ch = build_cumm_chart(
            ch_f, "Netto", "Cumm CH", plan_ch_val,
            "Cumulative Coal Hauling", "MT",
            cumm_pit, convert_kg=True, palette="ch",
        )
        st.plotly_chart(fig_ch, width="stretch")
