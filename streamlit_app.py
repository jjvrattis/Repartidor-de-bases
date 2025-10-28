import streamlit as st
import pandas as pd
import io

# --- Configuração da Página ---
st.set_page_config(
    page_title="Repartidor de Base CSV",
    page_icon="✂️",
    layout="centered"
)

# --- Título e Descrição ---
st.title("✂️ Repartidor de Base CSV")
st.markdown("""
Este aplicativo divide um arquivo CSV grande em vários arquivos menores de igual tamanho.
Ideal para processar lotes de dados ou enviar bases em partes.
""")

# --- Inicialização do Estado da Sessão ---
# Isso é crucial para que os arquivos gerados não desapareçam
if 'generated_files' not in st.session_state:
    st.session_state.generated_files = []

# --- Barra Lateral para Controles ---
st.sidebar.header("Configurações")

# 1. Upload do Arquivo
uploaded_file = st.sidebar.file_uploader(
    "Escolha um arquivo CSV",
    type=['csv'],
    help="Faça o upload da base de dados que você deseja dividir.",
    key="csv_uploader" # Chave única para o widget
)

# 2. Número de Divisões
if uploaded_file is not None:
    try:
        # Lê o arquivo para obter o número de linhas
        stringio = io.StringIO(uploaded_file.getvalue().decode('utf-8'))
        df_temp = pd.read_csv(stringio)
        total_rows = len(df_temp)
        st.sidebar.info(f"Seu arquivo tem **{total_rows:,}** linhas.")
        
        max_splits = total_rows
        num_splits = st.sidebar.number_input(
            "Em quantos lotes deseja dividir?",
            min_value=2,
            max_value=max_splits,
            value=10,
            step=1,
            help="O número total de arquivos que serão gerados."
        )
    except Exception as e:
        st.sidebar.error(f"Erro ao ler o arquivo: {e}")
        st.stop()
else:
    st.sidebar.info("Por favor, faça o upload de um arquivo para começar.")

# --- Botão de Ação Principal ---
if st.sidebar.button("🚀 Dividir Base", type="primary"):
    if uploaded_file is not None:
        # Limpa resultados anteriores
        st.session_state.generated_files = []

        # Re-lê o arquivo para processamento
        stringio = io.StringIO(uploaded_file.getvalue().decode('utf-8'))
        df = pd.read_csv(stringio)

        # --- NOVA FUNÇÃO: Padronizar CPF ---
        # Tenta encontrar a coluna 'CPF' (ignorando maiúsculas/minúsculas)
        cpf_col = None
        for col in df.columns:
            if 'cpf' in col.lower():
                cpf_col = col
                break
        
        if cpf_col:
            # Converte a coluna para string e preenche com zeros à esquerda até ter 11 dígitos
            df[cpf_col] = df[cpf_col].astype(str).str.zfill(11)
            st.success(f"✅ Coluna '{cpf_col}' encontrada e padronizada com 11 dígitos.")
        else:
            st.warning("⚠️ Nenhuma coluna com 'CPF' no nome foi encontrada. Os arquivos serão gerados sem a padronização de CPF.")

        total_rows = len(df)
        
        if num_splits > total_rows:
            st.error(f"Não é possível dividir {total_rows} linhas em {num_splits} arquivos.")
            st.stop()

        rows_per_split = total_rows // num_splits
        
        # Cria uma lista para armazenar os dados dos novos arquivos
        split_files = []

        # Loop para criar os lotes
        for i in range(num_splits):
            start_index = i * rows_per_split
            end_index = start_index + rows_per_split if i < num_splits - 1 else total_rows
            
            lote_df = df.iloc[start_index:end_index]
            
            csv_buffer = io.StringIO()
            lote_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            original_name = uploaded_file.name.replace('.csv', '')
            file_name = f"{original_name}_lote_{i+1}.csv"
            
            split_files.append({'filename': file_name, 'data': csv_data})

        # Armazena os arquivos gerados no estado da sessão
        st.session_state.generated_files = split_files
        st.success(f"Arquivo `{uploaded_file.name}` dividido em **{len(split_files)}** lotes com sucesso!")
        st.rerun() # Força uma reexecução para exibir os resultados imediatamente

# --- Área de Download dos Arquivos (Persistente) ---
if st.session_state.generated_files:
    st.subheader("📦 Arquivos Gerados")
    st.write("Clique nos botões abaixo para baixar cada lote:")

    for file_info in st.session_state.generated_files:
        st.download_button(
            label=f"📥 Baixar {file_info['filename']}",
            data=file_info['data'],
            file_name=file_info['filename'],
            mime='text/csv',
            key=file_info['filename'] # Key única para cada botão
        )

# --- Botão de Limpar ---
if st.session_state.generated_files:
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Limpar Painel"):
        st.session_state.generated_files = []
        st.rerun() # Recarrega a página para limpar a interface
