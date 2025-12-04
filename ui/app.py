"""
BCP Transaction Manager - Streamlit UI
Beautiful and functional interface for managing bank transactions
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from api_client import BCPApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="BCP Transaction Manager",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .dataframe {
        font-size: 0.9rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'api_client' not in st.session_state:
    st.session_state.api_client = BCPApiClient()

if 'transactions_df' not in st.session_state:
    st.session_state.transactions_df = None

if 'categories' not in st.session_state:
    st.session_state.categories = []

if 'edited_rows' not in st.session_state:
    st.session_state.edited_rows = {}


def load_transactions() -> pd.DataFrame:
    """Load all transactions from API"""
    try:
        with st.spinner("Cargando transacciones..."):
            transactions = st.session_state.api_client.get_all_transactions()
            
            if not transactions:
                st.warning("No se encontraron transacciones")
                return pd.DataFrame()
            
            df = pd.DataFrame(transactions)
            
            # Parse dates
            if 'fecha_proceso' in df.columns:
                df['fecha_proceso'] = pd.to_datetime(df['fecha_proceso'], format='%d/%m/%Y', errors='coerce')
            if 'fecha_consumo' in df.columns:
                df['fecha_consumo'] = pd.to_datetime(df['fecha_consumo'], format='%d/%m/%Y', errors='coerce')
            
            # Add month column for filtering
            if 'fecha_proceso' in df.columns:
                df['month'] = df['fecha_proceso'].dt.to_period('M')
            
            # Calculate amount (cargos are negative, abonos are positive)
            df['amount'] = df['abonos'] - df['cargos']
            
            logger.info(f"Loaded {len(df)} transactions")
            return df
            
    except Exception as e:
        st.error(f"Error cargando transacciones: {str(e)}")
        logger.error(f"Error loading transactions: {str(e)}")
        return pd.DataFrame()


def load_categories() -> List[Dict[str, Any]]:
    """Load all categories from API"""
    try:
        with st.spinner("Cargando categorías..."):
            categories = st.session_state.api_client.get_all_categories()
            logger.info(f"Loaded {len(categories)} categories")
            return categories
    except Exception as e:
        st.error(f"Error cargando categorías: {str(e)}")
        logger.error(f"Error loading categories: {str(e)}")
        return []


def save_transaction_update(transaction_id: str, history: str, category_name: Optional[str]) -> bool:
    """Save updates for a single transaction"""
    try:
        st.session_state.api_client.update_transaction(
            transaction_id=transaction_id,
            history=history if history else None,
            category_name=category_name if category_name else None
        )
        return True
    except Exception as e:
        st.error(f"Error guardando cambios: {str(e)}")
        logger.error(f"Error saving transaction {transaction_id}: {str(e)}")
        return False


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">💳 BCP Transaction Manager</div>', unsafe_allow_html=True)
    
    # Check API health
    if not st.session_state.api_client.health_check():
        st.error("⚠️ No se puede conectar con el API. Asegúrate de que el servidor esté corriendo en http://new-service:8000")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Reload button
        if st.button("🔄 Recargar Datos", use_container_width=True):
            st.session_state.transactions_df = None
            st.session_state.categories = []
            st.rerun()
        
        st.divider()
        
        # Stats
        st.subheader("📊 Estadísticas")
        if st.session_state.transactions_df is not None and not st.session_state.transactions_df.empty:
            df = st.session_state.transactions_df
            
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
    
    # Load data if not already loaded
    if st.session_state.transactions_df is None:
        st.session_state.transactions_df = load_transactions()
    
    if not st.session_state.categories:
        st.session_state.categories = load_categories()
    
    df = st.session_state.transactions_df
    
    if df.empty:
        st.info("👋 No hay transacciones para mostrar. Carga un PDF primero.")
        return
    
    # Filters
    st.subheader("🔍 Filtros")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Month filter
        available_months = sorted(df['month'].dropna().unique(), reverse=True)
        month_options = ["Todos"] + [str(m) for m in available_months]
        selected_month = st.selectbox(
            "Filtrar por Mes",
            options=month_options,
            index=0
        )
    
    with col2:
        # Category filter
        category_names = ["Todas"] + sorted(df['category_name'].dropna().unique().tolist())
        selected_category = st.selectbox(
            "Filtrar por Categoría",
            options=category_names,
            index=0
        )
    
    with col3:
        # Amount filter
        filter_type = st.selectbox(
            "Tipo",
            options=["Todos", "Cargos", "Abonos"],
            index=0
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_month != "Todos":
        filtered_df = filtered_df[filtered_df['month'] == pd.Period(selected_month)]
    
    if selected_category != "Todas":
        filtered_df = filtered_df[filtered_df['category_name'] == selected_category]
    
    if filter_type == "Cargos":
        filtered_df = filtered_df[filtered_df['cargos'] > 0]
    elif filter_type == "Abonos":
        filtered_df = filtered_df[filtered_df['abonos'] > 0]
    
    st.divider()
    
    # Display metrics for filtered data
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
    
    st.divider()
    
    # Transactions table
    st.subheader("📋 Transacciones")
    
    if filtered_df.empty:
        st.info("No hay transacciones que coincidan con los filtros seleccionados")
        return
    
    # Prepare display dataframe
    display_df = filtered_df[[
        'order', 'id', 'fecha_proceso', 'description', 'cargos', 'abonos', 
        'amount', 'category_name', 'history'
    ]].copy()
    
    display_df['fecha_proceso'] = display_df['fecha_proceso'].dt.strftime('%d/%m/%Y')
    display_df = display_df.rename(columns={
        'order': 'Orden',
        'id': '_ID',
        'fecha_proceso': 'Fecha',
        'description': 'Descripción',
        'cargos': 'Cargos (S/)',
        'abonos': 'Abonos (S/)',
        'amount': 'Monto Neto (S/)',
        'category_name': 'Categoría',
        'history': 'Historial'
    })
    
    # Show editable table
    st.info("💡 **Tip:** Haz clic en cualquier celda de 'Historial' o 'Categoría' para editarla")
    
    # Get category names for dropdown
    category_options = sorted([cat['name'] for cat in st.session_state.categories])
    
    # Display table with editing
    edited_df = st.data_editor(
        display_df,
        column_config={
            "Orden": st.column_config.NumberColumn("Orden", disabled=True, width="small"),
            "_ID": None,  # Hide the UUID column
            "Fecha": st.column_config.TextColumn("Fecha", disabled=True, width="small"),
            "Descripción": st.column_config.TextColumn("Descripción", disabled=True, width="large"),
            "Cargos (S/)": st.column_config.NumberColumn("Cargos (S/)", disabled=True, format="%.2f", width="small"),
            "Abonos (S/)": st.column_config.NumberColumn("Abonos (S/)", disabled=True, format="%.2f", width="small"),
            "Monto Neto (S/)": st.column_config.NumberColumn("Monto Neto (S/)", disabled=True, format="%.2f", width="small"),
            "Categoría": st.column_config.SelectboxColumn(
                "Categoría",
                options=category_options,
                width="medium",
                required=False
            ),
            "Historial": st.column_config.TextColumn(
                "Historial",
                width="large",
                max_chars=500
            ),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key="transaction_editor"
    )
    
    # Detect changes and show save button
    changes_detected = not display_df.equals(edited_df)
    
    if changes_detected:
        st.warning("⚠️ Tienes cambios sin guardar")
        
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                with st.spinner("Guardando cambios..."):
                    # Find changed rows
                    updates = []
                    for idx in range(len(display_df)):
                        if idx < len(edited_df):
                            orig_row = display_df.iloc[idx]
                            edited_row = edited_df.iloc[idx]
                            
                            if (orig_row['Historial'] != edited_row['Historial'] or 
                                orig_row['Categoría'] != edited_row['Categoría']):
                                
                                updates.append({
                                    "transaction_id": orig_row['_ID'],
                                    "history": edited_row['Historial'] if pd.notna(edited_row['Historial']) else "",
                                    "category_name": edited_row['Categoría'] if pd.notna(edited_row['Categoría']) else None
                                })
                    
                    if updates:
                        try:
                            result = st.session_state.api_client.batch_update_transactions(updates)
                            st.success(f"✅ {result.get('updated', 0)} transacciones actualizadas exitosamente!")
                            
                            # Reload data
                            st.session_state.transactions_df = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error guardando cambios: {str(e)}")
        
        with col2:
            if st.button("↩️ Descartar Cambios", use_container_width=True):
                st.rerun()


if __name__ == "__main__":
    main()
