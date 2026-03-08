"""
Raw Tables — Data tables display for production and plan data
"""
import streamlit as st

from calculations.formatting import safe_df


def render_raw_tables(ob_f, ch_f, ct_f, lt_ob, lt_coal, selected_date):
    """Render raw production data tables in tabs."""
    st.markdown('<div class="section-header">📋 Raw Data Tables</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["prod ob", "prod ch", "prod ct", "lt ob", "lt coal"]
    )

    with tab1:
        st.write(f"**prod ob** — {len(ob_f)} records (filtered)")
        st.dataframe(safe_df(ob_f), width="stretch", height=400)
    with tab2:
        st.write(f"**prod ch** — {len(ch_f)} records (filtered)")
        st.dataframe(safe_df(ch_f), width="stretch", height=400)
    with tab3:
        st.write(f"**prod ct** — {len(ct_f)} records (filtered)")
        st.dataframe(safe_df(ct_f), width="stretch", height=400)
    with tab4:
        lt_ob_f = lt_ob[lt_ob["Date"] == selected_date]
        st.write(f"**lt ob** — {len(lt_ob_f)} records")
        st.dataframe(safe_df(lt_ob_f), width="stretch", height=400)
    with tab5:
        lt_coal_f = lt_coal[lt_coal["Date"] == selected_date]
        st.write(f"**lt coal** — {len(lt_coal_f)} records")
        st.dataframe(safe_df(lt_coal_f), width="stretch", height=400)


def render_plan_tables(cumm_pit, plan_h_ob, plan_h_ch, selected_pit: str):
    """Render plan data tables in tabs."""
    st.markdown('<div class="section-header">📋 Plan Data</div>', unsafe_allow_html=True)

    tab_p1, tab_p2, tab_p3 = st.tabs(
        ["Cumm Plan Vol", "Plan Hourly OB", "Plan Hourly CH"]
    )

    with tab_p1:
        st.write(f"**Cumm Plan Vol** — PIT: {selected_pit}")
        st.dataframe(safe_df(cumm_pit), width="stretch")
    with tab_p2:
        st.dataframe(
            safe_df(plan_h_ob[plan_h_ob["PIT"] == selected_pit]),
            width="stretch",
        )
    with tab_p3:
        st.dataframe(
            safe_df(plan_h_ch[plan_h_ch["PIT"] == selected_pit]),
            width="stretch",
        )
