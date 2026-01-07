import pandas as pd
import requests
import os
import time
from datetime import datetime

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
INPUT_FILE = os.path.join(BASE_PATH, "data", "processed", "zarc_tratado.parquet")
OUTPUT_PATH = os.path.join(BASE_PATH, "data", "processed")

# Coordenadas Reais dos Municípios (Lat/Lon)
COORDENADAS = {
    "Rio Verde":  {"lat": -17.79, "lon": -50.92},
    "Jataí":      {"lat": -17.88, "lon": -51.71},
    "Cristalina": {"lat": -16.76, "lon": -47.61},
    "Mineiros":   {"lat": -17.56, "lon": -52.55},
    "Catalão":    {"lat": -18.17, "lon": -47.94}
}

def get_decendio(date_obj):
    """Calcula o decêndio (1-36) a partir de uma data."""
    day = date_obj.day
    month = date_obj.month
    
    # Decêndio dentro do mês (0, 1 ou 2)
    dec_mes = 0 if day <= 10 else (1 if day <= 20 else 2)
    
    # Decêndio do ano (1 a 36)
    return (month - 1) * 3 + dec_mes + 1

def buscar_clima_historico(cidade, lat, lon):
    """
    Busca 4 anos de dados reais no Open-Meteo e calcula a média por decêndio.
    """
    print(f"🌍 Baixando histórico real para {cidade}...")
    
    # URL da API de Histórico (Gratuita) - Pegando de 2020 a 2023
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2020-01-01",
        "end_date": "2023-12-31",
        "daily": ["temperature_2m_mean", "precipitation_sum"],
        "timezone": "America/Sao_Paulo"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        # Cria DataFrame temporário com os dados diários
        df_diario = pd.DataFrame({
            "time": data["daily"]["time"],
            "temp": data["daily"]["temperature_2m_mean"],
            "chuva": data["daily"]["precipitation_sum"]
        })
        
        # Converte para data real e calcula o decêndio de cada linha
        df_diario['date'] = pd.to_datetime(df_diario['time'])
        df_diario['decendio'] = df_diario['date'].apply(get_decendio)
        
        # AGRUPAMENTO (A Mágica da Climatologia)
        # Queremos saber: "Em média, quanto chove no decêndio 1 em Rio Verde?"
        climatologia = df_diario.groupby('decendio').agg({
            'temp': 'mean',          # Temperatura média do período
            'chuva': 'mean'          # Chuva média diária (multiplicaremos por 10 depois para ter o acumulado)
        }).reset_index()
        
        # A API retorna chuva diária média. O decêndio tem 10 dias.
        climatologia['chuva_acumulada_decendio'] = climatologia['chuva'] * 10
        climatologia['municipio'] = cidade
        
        return climatologia[['municipio', 'decendio', 'temp', 'chuva_acumulada_decendio']]

    except Exception as e:
        print(f"❌ Erro ao baixar dados para {cidade}: {e}")
        return None

def adicionar_dados_economicos(df):
    print("... Adicionando estimativas econômicas ...")
    tabela_precos = {
        "Soja": {"custo": 4500, "receita": 6500},
        "Milho": {"custo": 3800, "receita": 5200},
        "Banana": {"custo": 12000, "receita": 25000},
        "Laranja": {"custo": 15000, "receita": 30000},
        "Tomate Mesa": {"custo": 25000, "receita": 60000},
        "Alface": {"custo": 8000, "receita": 18000},
        "Cenoura": {"custo": 18000, "receita": 40000},
        "Pimentão": {"custo": 22000, "receita": 50000},
        "Abacaxi": {"custo": 14000, "receita": 32000},
        "Maracujá": {"custo": 16000, "receita": 35000}
    }
    df['custo_ha_est'] = df['cultura'].map(lambda x: tabela_precos.get(x, {}).get('custo', 0))
    df['receita_ha_est'] = df['cultura'].map(lambda x: tabela_precos.get(x, {}).get('receita', 0))
    df['roi_potencial'] = (df['receita_ha_est'] - df['custo_ha_est']) / df['custo_ha_est']
    return df

def main():
    print(f"--- Iniciando Enriquecimento com DADOS REAIS ---")
    
    # 1. Carregar ZARC
    if not os.path.exists(INPUT_FILE):
        print(f"ERRO: Arquivo {INPUT_FILE} não encontrado. Rode o passo 02.")
        return
    df_zarc = pd.read_parquet(INPUT_FILE)
    
    # 2. Baixar Clima para cada cidade (Loop)
    dfs_clima = []
    cidades_unicas = df_zarc['municipio'].unique()
    
    for cidade in cidades_unicas:
        if cidade in COORDENADAS:
            coords = COORDENADAS[cidade]
            df_clim = buscar_clima_historico(cidade, coords['lat'], coords['lon'])
            if df_clim is not None:
                dfs_clima.append(df_clim)
            # Pausa para ser gentil com a API
            time.sleep(1) 
    
    # Junta todos os dados climáticos num tabelão
    if not dfs_clima:
        print("Erro crítico: Nenhum dado climático baixado.")
        return
        
    df_clima_completo = pd.concat(dfs_clima)
    
    # 3. Cruzamento (Merge) ZARC + CLIMA
    # Juntamos pela chave composta: MUNICÍPIO + DECÊNDIO
    print("... Cruzando ZARC com CLIMA ...")
    df_final = pd.merge(
        df_zarc, 
        df_clima_completo, 
        on=['municipio', 'decendio'], 
        how='left'
    )
    
    # 4. Adicionar Economia
    df_final = adicionar_dados_economicos(df_final)
    
    # 5. Salvar
    arquivo_final = os.path.join(OUTPUT_PATH, "dataset_gold_mvp.parquet")
    df_final.to_parquet(arquivo_final, index=False)
    
    print(f"\n✅ SUCESSO! Dataset enriquecido salvo em: {arquivo_final}")
    print("Exemplo de dado real recuperado (Cristalina - Decêndio 1):")
    amostra = df_final[
        (df_final['municipio']=='Cristalina') & 
        (df_final['decendio']==1)
    ].head(1)
    print(amostra[['municipio', 'decendio', 'temp', 'chuva_acumulada_decendio']].to_string(index=False))

if __name__ == "__main__":
    main()