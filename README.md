# TaskFlow Pro 🚀

TaskFlow Pro é um gerenciador de tarefas completo, moderno e profissional desenvolvido em Python utilizando Streamlit, SQLite, Pandas e Plotly.

## Funcionalidades
- **Dashboard Interativo:** Indicadores de total de tarefas, concluídas, em andamento, pendentes e atrasadas, além de alertas rápidos.
- **CRUD Completo de Tarefas:** Cadastro, edição, exclusão e visualização detalhada com campos para título, descrição, projeto, prioridade, status e prazo.
- **Filtros Avançados:** Filtre por status, prioridade, projeto e pesquisa textual.
- **Gerenciamento de Projetos:** Cadastro e exclusão de projetos para organizar suas tarefas.
- **Relatórios Gráficos:** Visualizações interativas com Plotly (Status, Prioridade, Projetos).
- **Persistência Real:** Dados salvos localmente utilizando SQLite (`taskflow.db`).

## Requisitos
- Python 3.8 ou superior

## Instalação

1. Clone ou baixe este repositório para sua máquina.
2. Instale as dependências listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Como Executar

Execute o comando Streamlit no terminal na raiz do projeto:

```bash
streamlit run app.py
```

O aplicativo será aberto automaticamente no seu navegador padrão (geralmente em `http://localhost:8501`).
