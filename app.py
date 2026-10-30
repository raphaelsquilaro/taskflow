import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

from services.task_service import TaskService
from components.metrics import render_metrics_cards

# Page Configuration
st.set_page_config(
    page_title="TaskFlow Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    # Sidebar Navigation
    st.sidebar.markdown("# 🚀 TaskFlow Pro")
    st.sidebar.markdown("Gerenciador Profissional de Tarefas")
    st.sidebar.markdown("---")
    
    navigation = st.sidebar.radio(
        "Navegação",
        ["📊 Dashboard", "✅ Tarefas", "📁 Projetos", "📈 Relatórios"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Dica")
    st.sidebar.info("Cadastre projetos antes de criar tarefas para melhor organização.")

    if navigation == "📊 Dashboard":
        render_dashboard()
    elif navigation == "✅ Tarefas":
        render_tasks_page()
    elif navigation == "📁 Projetos":
        render_projects_page()
    elif navigation == "📈 Relatórios":
        render_reports_page()

def render_dashboard():
    st.markdown('<div class="main-header">Dashboard Geral</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Visão geral do progresso das suas tarefas e projetos.</div>', unsafe_allow_html=True)
    
    stats = TaskService.get_statistics()
    render_metrics_cards(stats)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    df = TaskService.get_tasks_dataframe()
    projects = TaskService.get_projects()
    
    with col1:
        st.subheader("📋 Tarefas Recentes")
        if not df.empty:
            recent_df = df.sort_values(by="created_at", ascending=False).head(5)
            st.dataframe(
                recent_df[["title", "project", "priority", "status", "due_date"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Nenhuma tarefa cadastrada ainda.")
            
    with col2:
        st.subheader("⚡ Ações Rápidas & Alertas")
        today_str = date.today().strftime("%Y-%m-%d")
        if not df.empty:
            overdue_tasks = df[(df["due_date"] < today_str) & (df["status"] != "Concluída")]
            if not overdue_tasks.empty:
                st.warning(f"⚠️ Você possui {len(overdue_tasks)} tarefa(s) atrasada(s)!")
                for _, row in overdue_tasks.head(3).iterrows():
                    st.markdown(f"- **{row['title']}** (Prazo: {row['due_date']})")
            else:
                st.success("🎉 Nenhuma tarefa atrasada no momento!")
        else:
            st.info("Cadastre tarefas para ver alertas de prazos.")
            
        st.markdown("---")
        st.metric("Total de Projetos Cadastrados", len(projects))

def render_tasks_page():
    st.markdown('<div class="main-header">Gerenciamento de Tarefas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Crie, edite, filtre e gerencie todas as suas atividades.</div>', unsafe_allow_html=True)
    
    projects = TaskService.get_projects()
    project_names = [p["name"] for p in projects]
    
    if not project_names:
        st.warning("⚠️ Nenhum projeto cadastrado. Por favor, cadastre ao menos um projeto na aba 'Projetos' antes de criar tarefas.")
        return

    # Tabs for Add vs List/Edit
    tab_list, tab_add = st.tabs(["📋 Lista de Tarefas", "➕ Nova Tarefa"])
    
    with tab_add:
        st.subheader("Cadastrar Nova Tarefa")
        with st.form("form_add_task", clear_on_submit=True):
            title = st.text_input("Título da Tarefa *")
            description = st.text_area("Descrição")
            
            col_a, col_b = st.columns(2)
            with col_a:
                project = st.selectbox("Projeto *", options=project_names)
                priority = st.selectbox("Prioridade", options=["Baixa", "Média", "Alta", "Urgente"])
            with col_b:
                status = st.selectbox("Status", options=["Pendente", "Em Andamento", "Concluída", "Cancelada"])
                due_date = st.date_input("Data de Prazo", value=date.today())
                
            submitted = st.form_submit_button("Salvar Tarefa")
            if submitted:
                try:
                    TaskService.add_task(title, description, project, priority, status, due_date)
                    st.success("Tarefa cadastrada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar tarefa: {e}")

    with tab_list:
        st.subheader("Filtrar e Gerenciar Tarefas")
        
        df = TaskService.get_tasks_dataframe()
        if df.empty:
            st.info("Nenhuma tarefa cadastrada.")
            return
            
        # Filters
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            status_filter = st.selectbox("Filtrar por Status", options=["Todos"] + list(df["status"].unique()))
        with col_f2:
            priority_filter = st.selectbox("Filtrar por Prioridade", options=["Todos"] + list(df["priority"].unique()))
        with col_f3:
            proj_filter = st.selectbox("Filtrar por Projeto", options=["Todos"] + list(df["project"].unique()))
        with col_f4:
            search_query = st.text_input("Pesquisar Título", "")
            
        filtered_df = df.copy()
        if status_filter != "Todos":
            filtered_df = filtered_df[filtered_df["status"] == status_filter]
        if priority_filter != "Todos":
            filtered_df = filtered_df[filtered_df["priority"] == priority_filter]
        if proj_filter != "Todos":
            filtered_df = filtered_df[filtered_df["project"] == proj_filter]
        if search_query.strip():
            filtered_df = filtered_df[filtered_df["title"].str.contains(search_query, case=False, na=False)]
            
        st.markdown(f"Exibindo **{len(filtered_df)}** de **{len(df)}** tarefas.")
        
        for _, row in filtered_df.iterrows():
            with st.expander(f"📌 [{row['status']}] {row['title']} (Projeto: {row['project']} | Prazo: {row['due_date']})"):
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    st.write(f"**Descrição:** {row['description'] if row['description'] else 'Nenhuma descrição.'}")
                    st.write(f"**Prioridade:** {row['priority']} | **Criada em:** {row['created_at']}")
                with col_d2:
                    if st.button("Excluir", key=f"del_{row['id']}"):
                        try:
                            TaskService.delete_task(row['id'])
                            st.success("Tarefa excluída!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")
                            
                # Edit Form inside expander or modal
                with st.form(f"form_edit_{row['id']}"):
                    st.markdown("### Editar Tarefa")
                    new_title = st.text_input("Título", value=row["title"], key=f"title_{row['id']}")
                    new_desc = st.text_area("Descrição", value=row["description"] if row["description"] else "", key=f"desc_{row['id']}")
                    
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        curr_proj_idx = project_names.index(row["project"]) if row["project"] in project_names else 0
                        new_proj = st.selectbox("Projeto", options=project_names, index=curr_proj_idx, key=f"proj_{row['id']}")
                    with ec2:
                        priorities = ["Baixa", "Média", "Alta", "Urgente"]
                        curr_prio_idx = priorities.index(row["priority"]) if row["priority"] in priorities else 0
                        new_prio = st.selectbox("Prioridade", options=priorities, index=curr_prio_idx, key=f"prio_{row['id']}")
                    with ec3:
                        statuses = ["Pendente", "Em Andamento", "Concluída", "Cancelada"]
                        curr_stat_idx = statuses.index(row["status"]) if row["status"] in statuses else 0
                        new_stat = st.selectbox("Status", options=statuses, index=curr_stat_idx, key=f"stat_{row['id']}")
                        
                    parsed_date = datetime.strptime(row["due_date"], "%Y-%m-%d").date() if isinstance(row["due_date"], str) else row["due_date"]
                    new_due = st.date_input("Prazo", value=parsed_date, key=f"due_{row['id']}")
                    
                    if st.form_submit_button("Atualizar Tarefa"):
                        try:
                            TaskService.update_task(row["id"], new_title, new_desc, new_proj, new_prio, new_stat, new_due)
                            st.success("Tarefa atualizada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {e}")

def render_projects_page():
    st.markdown('<div class="main-header">Gerenciamento de Projetos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Cadastre e organize seus projetos para categorizar as tarefas.</div>', unsafe_allow_html=True)
    
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.subheader("Novo Projeto")
        with st.form("form_add_project", clear_on_submit=True):
            p_name = st.text_input("Nome do Projeto *")
            p_desc = st.text_area("Descrição do Projeto")
            submitted_p = st.form_submit_button("Criar Projeto")
            if submitted_p:
                try:
                    TaskService.add_project(p_name, p_desc)
                    st.success("Projeto criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar projeto: {e}")
                    
    with col_list:
        st.subheader("Projetos Cadastrados")
        projects = TaskService.get_projects()
        if not projects:
            st.info("Nenhum projeto cadastrado.")
        else:
            for p in projects:
                with st.container():
                    st.markdown(f"### 📁 {p['name']}")
                    st.write(f"**Descrição:** {p['description'] if p['description'] else 'Sem descrição.'}")
                    st.write(f"**Criado em:** {p['created_at']}")
                    if st.button("Excluir Projeto", key=f"del_proj_{p['id']}"):
                        try:
                            TaskService.delete_project(p['id'])
                            st.success("Projeto excluído!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir projeto: {e}")
                    st.markdown("---")

def render_reports_page():
    st.markdown('<div class="main-header">Relatórios & Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Análise detalhada de desempenho e distribuição de tarefas.</div>', unsafe_allow_html=True)
    
    df = TaskService.get_tasks_dataframe()
    if df.empty:
        st.info("Nenhum dado disponível para gerar relatórios.")
        return
        
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tarefas por Status")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Quantidade"]
        fig_status = px.pie(status_counts, names="Status", values="Quantidade", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_status, use_container_width=True)
        
    with col2:
        st.subheader("Tarefas por Prioridade")
        priority_counts = df["priority"].value_counts().reset_index()
        priority_counts.columns = ["Prioridade", "Quantidade"]
        fig_prio = px.bar(priority_counts, x="Prioridade", y="Quantidade", color="Prioridade", color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_prio, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("Tarefas por Projeto")
    proj_counts = df["project"].value_counts().reset_index()
    proj_counts.columns = ["Projeto", "Quantidade"]
    fig_proj = px.bar(proj_counts, x="Projeto", y="Quantidade", text="Quantidade", color="Projeto", color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig_proj, use_container_width=True)

if __name__ == "__main__":
    main()
