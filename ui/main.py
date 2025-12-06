"""
BCP Transaction Manager - Streamlit UI
Clean Architecture Implementation
"""
import streamlit as st
import pandas as pd
import logging

# Infrastructure
from infrastructure.api_transaction_repository import ApiTransactionRepository
from infrastructure.api_category_repository import ApiCategoryRepository
from infrastructure.local_file_repository import LocalFileRepository

# Use Cases
from use_cases.transaction_use_cases import (
    GetTransactionsUseCase,
    GetCategoriesUseCase,
    BatchUpdateTransactionsUseCase
)
from use_cases.file_use_cases import SaveFileUseCase

# Presentation
from presentation.ui_components import render_header, render_stats, render_filters, render_metrics
from presentation.styles import CUSTOM_CSS

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

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_dependencies():
    """Initialize dependencies (Dependency Injection)"""
    if 'repositories' not in st.session_state:
        st.session_state.repositories = {
            'transaction': ApiTransactionRepository(),
            'category': ApiCategoryRepository(),
            'file': LocalFileRepository()
        }
    
    if 'use_cases' not in st.session_state:
        repos = st.session_state.repositories
        st.session_state.use_cases = {
            'get_transactions': GetTransactionsUseCase(repos['transaction']),
            'get_categories': GetCategoriesUseCase(repos['category']),
            'batch_update': BatchUpdateTransactionsUseCase(repos['transaction']),
            'save_file': SaveFileUseCase(repos['file'])
        }


def init_session_state():
    """Initialize session state"""
    if 'transactions_df' not in st.session_state:
        st.session_state.transactions_df = None
    
    if 'categories' not in st.session_state:
        st.session_state.categories = []


def handle_file_upload(save_file_use_case):
    """Handle file upload"""
    st.subheader("📄 Subir PDF")
    uploaded_file = st.file_uploader(
        "Selecciona un archivo PDF de transacciones BCP",
        type=['pdf'],
        help="Sube el PDF del estado de cuenta de BCP"
    )
    
    if uploaded_file is not None:
        if st.button("💾 Guardar PDF", use_container_width=True):
            try:
                file_path = save_file_use_case.execute(uploaded_file.getbuffer(), uploaded_file.name)
                st.success(f"✅ Archivo guardado: {uploaded_file.name}")
                logger.info(f"File saved: {file_path}")
            except Exception as e:
                st.error(f"❌ Error guardando archivo: {str(e)}")
                logger.error(f"Error saving file: {str(e)}")


def apply_filters(df, selected_month, selected_category, filter_type):
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    if selected_month != "Todos":
        filtered_df = filtered_df[filtered_df['month'] == pd.Period(selected_month)]
    
    if selected_category != "Todas":
        filtered_df = filtered_df[filtered_df['category_name'] == selected_category]
    
    if filter_type == "Cargos":
        filtered_df = filtered_df[filtered_df['cargos'] > 0]
    elif filter_type == "Abonos":
        filtered_df = filtered_df[filtered_df['abonos'] > 0]
    
    return filtered_df


def prepare_display_dataframe(filtered_df):
    """Prepare dataframe for display"""
    # Sort by order
    filtered_df = filtered_df.sort_values('order', ascending=True)
    
    # Select and prepare columns
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
    
    return display_df


def extract_updates(display_df, edited_df):
    """Extract updates from edited dataframe"""
    updates = []
    
    for idx in range(len(display_df)):
        if idx < len(edited_df):
            orig_row = display_df.iloc[idx]
            edited_row = edited_df.iloc[idx]
            
            if (orig_row['Historial'] != edited_row['Historial'] or 
                orig_row['Categoría'] != edited_row['Categoría']):
                
                # Extract scalar values
                history_raw = edited_row['Historial']
                category_raw = edited_row['Categoría']
                
                # Handle lists
                if isinstance(history_raw, list):
                    history_raw = history_raw[0] if len(history_raw) > 0 else ""
                if isinstance(category_raw, list):
                    category_raw = category_raw[0] if len(category_raw) > 0 else None
                
                # Convert to strings
                if pd.notna(history_raw) and history_raw != "":
                    history_val = str(history_raw)
                else:
                    history_val = ""
                    
                if pd.notna(category_raw) and category_raw != "":
                    category_val = str(category_raw)
                else:
                    category_val = None
                
                updates.append({
                    "transaction_id": str(orig_row['_ID']),
                    "history": history_val,
                    "category_name": category_val
                })
    
    return updates


def main():
    """Main application"""
    # Initialize
    init_dependencies()
    init_session_state()
    
    use_cases = st.session_state.use_cases
    repos = st.session_state.repositories
    
    # Header
    render_header()
    
    # Check API health
    if not repos['transaction'].health_check():
        st.error("⚠️ No se puede conectar con el API. Asegúrate de que el servidor esté corriendo en http://new-service:8000")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # File upload
        handle_file_upload(use_cases['save_file'])
        
        st.divider()
        
        # Reload button
        if st.button("🔄 Recargar Datos", use_container_width=True):
            st.session_state.transactions_df = None
            st.session_state.categories = []
            st.rerun()
        
        st.divider()
        
        # Stats
        render_stats(st.session_state.transactions_df)
    
    # Load data
    if st.session_state.transactions_df is None:
        try:
            with st.spinner("Cargando transacciones..."):
                st.session_state.transactions_df = use_cases['get_transactions'].execute()
        except Exception as e:
            st.error(f"Error cargando transacciones: {str(e)}")
            return
    
    if not st.session_state.categories:
        try:
            with st.spinner("Cargando categorías..."):
                st.session_state.categories = use_cases['get_categories'].execute()
        except Exception as e:
            st.error(f"Error cargando categorías: {str(e)}")
            return
    
    df = st.session_state.transactions_df
    
    if df.empty:
        st.info("👋 No hay transacciones para mostrar. Carga un PDF primero.")
        return
    
    # Filters
    selected_month, selected_category, filter_type = render_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df, selected_month, selected_category, filter_type)
    
    st.divider()
    
    # Display metrics
    render_metrics(filtered_df)
    
    st.divider()
    
    # Transactions table
    st.subheader("📋 Transacciones")
    
    if filtered_df.empty:
        st.info("No hay transacciones que coincidan con los filtros seleccionados")
        return
    
    # Prepare display
    display_df = prepare_display_dataframe(filtered_df)
    
    st.info("💡 **Tip:** Haz clic en cualquier celda de 'Historial' o 'Categoría' para editarla")
    
    # Get category options
    category_options = sorted([cat['name'] for cat in st.session_state.categories])
    
    # Display editable table
    edited_df = st.data_editor(
        display_df,
        column_config={
            "Orden": st.column_config.NumberColumn("Orden", disabled=True, width="small"),
            "_ID": None,
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
            "Historial": st.column_config.TextColumn("Historial", width="large", max_chars=500),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key="transaction_editor"
    )
    
    # Handle changes
    changes_detected = not display_df.equals(edited_df)
    
    if changes_detected:
        st.warning("⚠️ Tienes cambios sin guardar")
        
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                with st.spinner("Guardando cambios..."):
                    updates = extract_updates(display_df, edited_df)
                    
                    if updates:
                        try:
                            result = use_cases['batch_update'].execute(updates)
                            st.success(f"✅ {result.get('updated', 0)} transacciones actualizadas exitosamente!")
                            
                            # Reload
                            st.session_state.transactions_df = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error guardando cambios: {str(e)}")
        
        with col2:
            if st.button("↩️ Descartar Cambios", use_container_width=True):
                st.rerun()


if __name__ == "__main__":
    main()
