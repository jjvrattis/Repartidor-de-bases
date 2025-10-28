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

# --- Barra Lateral para Controles ---
st.sidebar.header("Configurações")

# 1. Upload do Arquivo
uploaded_file = st.sidebar.file_uploader(
    "Escolha um arquivo CSV",
    type=['csv'],
    help="Faça o upload da base de dados que você deseja dividir."
)

# 2. Número de Divisões
if uploaded_file is not None:
    # Lê o arquivo apenas para obter o número de linhas e mostrar ao usuário
    try:
        # Usando chunksize para não carregar o arquivo inteiro na memória só para contar linhas
        # Mas para este app, carregar tudo é mais simples e suficiente.
        df_temp = pd.read_csv(uploaded_file)
        total_rows = len(df_temp)
        st.sidebar.info(f"Seu arquivo tem **{total_rows:,}** linhas.")
        
        max_splits = total_rows
        num_splits = st.sidebar.number_input(
            "Em quantos lotes deseja dividir?",
            min_value=2,
            max_value=max_splits,
            value=10, # Valor padrão
            step=1,
            help="O número total de arquivos que serão gerados."
        )
    except Exception as e:
        st.sidebar.error(f"Erro ao ler o arquivo: {e}")
        st.stop()
else:
    st.sidebar.info("Por favor, faça o upload de um arquivo para começar.")
    st.stop() # Para a execução se não houver arquivo

# --- Botão de Ação ---
if st.sidebar.button("🚀 Dividir Base"):
    if uploaded_file is not None:
        # Re-lê o arquivo para processamento (o cursor do arquivo pode ter mudado)
        # Usamos io.StringIO para tratar o upload como um arquivo em memória
        stringio = io.StringIO(uploaded_file.getvalue().decode('utf-8'))
        df = pd.read_csv(stringio)

        total_rows = len(df)
        
        # Validação para não dividir em mais partes que linhas
        if num_splits > total_rows:
            st.error(f"Não é possível dividir {total_rows} linhas em {num_splits} arquivos.")
            st.stop()

        # Calcula o número de linhas por lote
        rows_per_split = total_rows // num_splits
        
        st.success(f"Dividindo o arquivo `{uploaded_file.name}` em **{num_splits}** lotes de aproximadamente **{rows_per_split}** linhas cada.")

        # Cria uma lista para armazenar os dados dos novos arquivos
        split_files = []

        # Loop para criar os lotes
        for i in range(num_splits):
            start_index = i * rows_per_split
            # O último lote pega o resto das linhas, se houver
            end_index = start_index + rows_per_split if i < num_splits - 1 else total_rows
            
            # Fatia o DataFrame
            lote_df = df.iloc[start_index:end_index]
            
            # Converte o lote para CSV em memória (sem o índice)
            csv_buffer = io.StringIO()
            lote_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Define o nome do arquivo
            original_name = uploaded_file.name.replace('.csv', '')
            file_name = f"{original_name}_lote_{i+1}.csv"
            
            # Adiciona à lista de arquivos para download
            split_files.append({'filename': file_name, 'data': csv_data})

        # --- Área de Download dos Arquivos ---
        st.subheader("📦 Arquivos Gerados")
        st.write("Clique nos botões abaixo para baixar cada lote:")

        # Exibe um botão de download para cada arquivo gerado
        for file_info in split_files:
            st.download_button(
                label=f"📥 Baixar {file_info['filename']}",
                data=file_info['data'],
                file_name=file_info['filename'],
                mime='text/csv',
                key=file_info['filename'] # Key única para cada botão
            )
    else:
        st.warning("Por favor, faça o upload de um arquivo primeiro.")
