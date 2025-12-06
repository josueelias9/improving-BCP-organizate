"""
UI Components - Reusable Streamlit components
"""
import streamlit as st


def render_header():
    """Render application header"""
    st.markdown('<div class="main-header">💳 BCP Transaction Manager</div>', unsafe_allow_html=True)


def render_stats(df):
    """Render statistics sidebar"""
    st.subheader("📊 Estadísticas")
    
    if df is not None and not df.empty:
        total_transactions = len(df)
        total_cargos = df['cargos'].sum()
        total_abonos = df['abonos'].sum()
        balance = total_abonos - total_cargos
        
        st.metric("Total Transacciones", f"{total_transactions}")
        st.metric("Total Cargos", f"S/ {total_cargos:,.2f}", delta_color="inverse")
        st.metric("Total Abonos", f"S/ {total_abonos:,.2f}")
        st.metric("Balance Neto", f"S/ {balance:,.2f}", 
                 delta=f"{balance:,.2f}", 
                 delta_color="normal" if balance >= 0 else "inverse")


def render_filters(df):
    """Render filter controls"""
    st.subheader("🔍 Filtros")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        available_months = sorted(df['month'].dropna().unique(), reverse=True)
        month_options = ["Todos"] + [str(m) for m in available_months]
        selected_month = st.selectbox("Filtrar por Mes", options=month_options, index=0)
    
    with col2:
        category_names = ["Todas"] + sorted(df['category_name'].dropna().unique().tolist())
        selected_category = st.selectbox("Filtrar por Categoría", options=category_names, index=0)
    
    with col3:
        filter_type = st.selectbox("Tipo", options=["Todos", "Cargos", "Abonos"], index=0)
    
    return selected_month, selected_category, filter_type


def render_metrics(filtered_df):
    """Render filtered metrics"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Transacciones Filtradas", len(filtered_df))
    with col2:
        st.metric("Cargos", f"S/ {filtered_df['cargos'].sum():,.2f}")
    with col3:
        st.metric("Abonos", f"S/ {filtered_df['abonos'].sum():,.2f}")
    with col4:
        balance = filtered_df['abonos'].sum() - filtered_df['cargos'].sum()
        st.metric("Balance", f"S/ {balance:,.2f}")
