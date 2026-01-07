import pandas as pd
import os

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
RAW_FILE = os.path.join(BASE_PATH, "data", "raw", "zarc_goias_bruto.csv")
PROCESSED_PATH = os.path.join(BASE_PATH, "data", "processed")

os.makedirs(PROCESSED_PATH, exist_ok=True)

def converter_decendio_para_data(decendio):
    """
    Transforma o número do decêndio (1-36) em um rótulo legível.
    Ex: 1 -> "Jan/Início"
    """
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    # Matemática do decêndio:
    # Decêndio 1, 2, 3 -> Mês 0 (Jan)
    indice_mes = (decendio - 1) // 3
    parte = (decendio - 1) % 3 # 0=Início, 1=Meio, 2=Fim
    
    sufixos = ["Início", "Meio", "Fim"]
    
    return f"{meses[indice_mes]}/{sufixos[parte]}"

def processar_dados():
    print(f"--- Iniciando Processamento (Limpeza) ---")
    
    # 1. Leitura do CSV Bruto
    if not os.path.exists(RAW_FILE):
        print("ERRO: Arquivo bruto não encontrado. Rode o passo 01 primeiro.")
        return

    df = pd.read_csv(RAW_FILE, sep=";", encoding="utf-8")
    print(f"Lido arquivo bruto com {len(df)} linhas.")

    # 2. Engenharia de Features (Criar colunas novas)
    
    # A. Tratamento do Risco (Para IA/Gráficos)
    # Cria uma coluna numérica: 20, 30, 40. Se for INAPTO, vira 100.
    df['risco_numerico'] = df['risco'].apply(lambda x: 100 if x == 'INAPTO' else int(x))
    
    # B. Flag de Viabilidade (Binário)
    # 1 = Plantável (Risco <= 40), 0 = Não Plantável
    df['e_plantavel'] = df['risco_numerico'].apply(lambda x: 1 if x <= 40 else 0)

    # C. Data Legível
    df['periodo_legivel'] = df['decendio'].apply(converter_decendio_para_data)

    # D. Descrição do Solo
    mapa_solo = {
        "AD1": "Arenoso (Risco Alto)",
        "AD2": "Médio",
        "AD3": "Argiloso (Risco Baixo)"
    }
    df['solo_desc'] = df['solo'].map(mapa_solo)

    # 3. Salvamento Otimizado (Parquet)
    arquivo_destino = os.path.join(PROCESSED_PATH, "zarc_tratado.parquet")
    
    # O Parquet mantém os tipos de dados (int fica int, string fica string)
    df.to_parquet(arquivo_destino, index=False)
    
    print(f"✅ Processamento concluído!")
    print(f"Arquivo limpo salvo em: {arquivo_destino}")
    print("Amostra dos dados tratados:")
    print(df[['cultura', 'periodo_legivel', 'risco', 'risco_numerico']].head())

if __name__ == "__main__":
    processar_dados()