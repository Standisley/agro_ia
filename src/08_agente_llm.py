import os
import pandas as pd
import joblib
import chromadb
from chromadb.utils import embedding_functions

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
DB_PATH = os.path.join(BASE_PATH, "data", "chroma_db")
MODEL_PATH = os.path.join(BASE_PATH, "models", "modelo_produtividade.joblib")
PARQUET_PATH = os.path.join(BASE_PATH, "data", "processed", "dataset_gold_mvp.parquet")

print("🚀 Inicializando Agente Híbrido (ML + RAG + LLM)...")

client = chromadb.PersistentClient(path=DB_PATH)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name="manual_tecnico_agricola", embedding_function=emb_fn)

modelo_ml = joblib.load(MODEL_PATH)
df_zarc = pd.read_parquet(PARQUET_PATH)

# --- CORREÇÃO DE COLUNAS NO AGENTE TAMBÉM ---
mapa_colunas = {
    'chuva_acumulada_decendio': 'chuva_media_mm',
    'temp': 'temp_media_c'
}
df_zarc.rename(columns=mapa_colunas, inplace=True)

MAPA_ARQUIVOS = {
    "Soja": "soja_manual_tecnico", "Milho": "milho_safrinha_manual",
    "Banana": "banana_irrigada", "Laranja": "laranja_citros",
    "Tomate Mesa": "tomate_mesa_manual", "Cenoura": "cenoura_cerrado_manual",
    "Pimentão": "pimentao_campo_aberto", "Abacaxi": "abacaxi_perola",
    "Maracujá": "maracuja_azedo", "Alface": "alface_hidroponia_campo"
}

def chamar_llm_real(prompt):
    return f"""
    [RESPOSTA SIMULADA DA LLM]
    Olá! Sou seu assistente AgroIA.
    
    A previsão de produtividade é de {prompt.split('Produtividade Prevista:')[1].split()[0]} sacas/ha, considerando o risco climático atual.
    
    Sobre sua dúvida técnica:
    {prompt.split('CONTEXTO TÉCNICO (EMBRAPA):')[1][:300]}...
    
    Recomendo monitorar o clima local.
    """

def agente_supremo(pergunta, cidade, cultura):
    print(f"\n🧠 Processando: '{pergunta}' | {cultura} em {cidade}...")
    
    # 1. Dados
    filtro = df_zarc[(df_zarc['municipio'] == cidade) & (df_zarc['cultura'] == cultura)]
    if filtro.empty: return "Sem dados ZARC encontrados."
    dado_real = filtro.sort_values('risco_numerico').iloc[0]
    
    # 2. ML Predict
    solo_map = {"AD1": 1, "AD2": 2, "AD3": 3}
    solo_val = solo_map.get(dado_real['solo'], 2)
    
    # Agora usa os nomes corrigidos
    input_ml = [[
        dado_real['risco_numerico'], 
        dado_real['chuva_media_mm'], 
        dado_real['temp_media_c'], 
        dado_real['custo_ha_est'],
        solo_val
    ]]
    
    previsao = modelo_ml.predict(input_ml)[0]
    
    # 3. RAG
    arquivo_alvo = MAPA_ARQUIVOS.get(cultura)
    docs = collection.query(query_texts=[pergunta], n_results=1, where={"topico": arquivo_alvo})
    texto_tecnico = docs['documents'][0][0] if docs['documents'] else "Sem manual."

    # 4. Prompt
    prompt = f"""
    Cultura: {cultura} | Cidade: {cidade}
    Produtividade Prevista: {previsao:.1f}
    CONTEXTO TÉCNICO (EMBRAPA):
    {texto_tecnico}
    """
    
    return chamar_llm_real(prompt)

if __name__ == "__main__":
    resp = agente_supremo("Quais doenças devo preocupar?", "Rio Verde", "Soja")
    print(resp)