import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
PARQUET_PATH = os.path.join(BASE_PATH, "data", "processed", "dataset_gold_mvp.parquet")
MODEL_PATH = os.path.join(BASE_PATH, "models")

os.makedirs(MODEL_PATH, exist_ok=True)

def treinar_modelo_produtividade():
    print("--- 🧠 Treinando IA Preditiva (Random Forest) ---")
    
    # 1. Carregar Dados
    if not os.path.exists(PARQUET_PATH):
        print("Erro: Dataset não encontrado.")
        return
    
    df = pd.read_parquet(PARQUET_PATH)
    print(f"Dados carregados. Colunas originais: {df.columns.tolist()}")

    # --- CORREÇÃO DE COLUNAS (O FIX DO ERRO) ---
    # Se os dados vieram do Open-Meteo, renomeamos para o padrão que o modelo espera
    mapa_colunas = {
        'chuva_acumulada_decendio': 'chuva_media_mm',
        'chuva': 'chuva_media_mm',
        'temp': 'temp_media_c',
        'temperature_2m_mean': 'temp_media_c'
    }
    df.rename(columns=mapa_colunas, inplace=True)
    
    # Verifica se deu certo
    if 'chuva_media_mm' not in df.columns or 'temp_media_c' not in df.columns:
        print("❌ ERRO CRÍTICO: Não encontrei colunas de clima (chuva/temp).")
        print("Colunas atuais:", df.columns.tolist())
        return

    # 2. Engenharia de Features
    mapa_solo = {"AD1": 1, "AD2": 2, "AD3": 3} 
    df['solo_num'] = df['solo'].map(mapa_solo).fillna(2)
    
    # Target Sintético (Lógica de Negócio para o MVP)
    print("... Gerando alvo de produtividade ...")
    df['produtividade_esperada'] = 100 - (df['risco_numerico'] * 0.8) + (df['solo_num'] * 5)
    df['produtividade_esperada'] += np.random.normal(0, 5, size=len(df))
    
    # Seleção de Features
    features = ['risco_numerico', 'chuva_media_mm', 'temp_media_c', 'custo_ha_est', 'solo_num']
    target = 'produtividade_esperada'
    
    X = df[features].fillna(0)
    y = df[target]
    
    # 3. Treinamento
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 4. Avaliação
    predicoes = model.predict(X_test)
    erro = mean_absolute_error(y_test, predicoes)
    
    print(f"✅ Modelo Treinado com Sucesso!")
    print(f"📊 Erro Médio Absoluto (MAE): +/- {erro:.2f}")
    
    # 5. Salvar o Modelo
    caminho_modelo = os.path.join(MODEL_PATH, "modelo_produtividade.joblib")
    joblib.dump(model, caminho_modelo)
    print(f"💾 Modelo salvo em: {caminho_modelo}")

if __name__ == "__main__":
    treinar_modelo_produtividade()