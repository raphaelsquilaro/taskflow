import streamlit as st

def render_metrics_cards(stats):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="Total de Tarefas", value=stats["total"])
    with col2:
        st.metric(label="Concluídas", value=stats["completed"])
    with col3:
        st.metric(label="Em Andamento", value=stats["in_progress"])
    with col4:
        st.metric(label="Pendentes", value=stats["pending"])
    with col5:
        st.metric(label="Atrasadas", value=stats["overdue"], delta=f"-{stats['overdue']}" if stats["overdue"] > 0 else None, delta_color="inverse")
