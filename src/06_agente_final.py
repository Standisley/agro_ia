import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
DB_PATH = os.path.join(BASE_PATH, "data", "chroma_db")
PARQUET_PATH = os.path.join(BASE_PATH, "data", "processed", "dataset_gold_mvp.parquet")

print("🤖 Inicializando Agente AgroIA (Com Filtro de Contexto)...")

client = chromadb.PersistentClient(path=DB_PATH)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_collection(name="manual_tecnico_agricola", embedding_function=emb_fn)

if os.path.exists(PARQUET_PATH):
    df_zarc = pd.read_parquet(PARQUET_PATH)
else:
    df_zarc = pd.DataFrame()

# --- MAPA DE CONTEXTO ---
# Conecta o nome simples (App) ao nome do arquivo técnico (Banco)
# Isso garante que quem pede SOJA não receba dica de MARACUJÁ.
MAPA_ARQUIVOS = {
    "Soja": "soja_manual_tecnico",
    "Milho": "milho_safrinha_manual",
    "Banana": "banana_irrigada",
    "Laranja": "laranja_citros",
    "Tomate Mesa": "tomate_mesa_manual",
    "Cenoura": "cenoura_cerrado_manual",
    "Pimentão": "pimentao_campo_aberto",
    "Abacaxi": "abacaxi_perola",
    "Maracujá": "maracuja_azedo",
    "Alface": "alface_hidroponia_campo"
}

def buscar_conhecimento_tecnico(pergunta, cultura_filtro):
    """
    Busca no ChromaDB aplicando FILTRO por cultura.
    Assim a IA não mistura Maracujá com Soja.
    """
    # Descobre qual o arquivo técnico correto
    arquivo_alvo = MAPA_ARQUIVOS.get(cultura_filtro)
    
    if not arquivo_alvo:
        return f"⚠️ Sem manual técnico cadastrado para {cultura_filtro}."

    # AQUI ESTÁ O PULO DO GATO: where={"topico": ...}
    results = collection.query(
        query_texts=[pergunta],
        n_results=2,
        where={"topico": arquivo_alvo} # <--- O Filtro Rígido
    )
    
    contexto = ""
    if results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            contexto += f"- {doc}\n\n"
    else:
        contexto = "Não encontrei informações específicas no manual sobre isso."
    
    return contexto

def buscar_dados_zarc(cidade, cultura):
    if df_zarc.empty: return "Dados ZARC indisponíveis."
    
    filtro = df_zarc[
        (df_zarc['municipio'] == cidade) & 
        (df_zarc['cultura'] == cultura)
    ]
    
    if filtro.empty:
        return f"Sem dados ZARC para {cultura}."
    
    melhor = filtro.sort_values('risco_numerico').iloc[0]
    
    return f"""
    📊 VIABILIDADE ECONÔMICA (ZARC):
    - Melhor Janela: {melhor['periodo_legivel']}
    - Risco: {melhor['risco_numerico']}%
    - Custo: R$ {melhor['custo_ha_est']:.2f}/ha
    - Solo Ideal: {melhor['solo_desc']}
    """

def agente_consultor(pergunta, cidade, cultura):
    print("\n" + "="*60)
    print(f"👤 PERGUNTA: {pergunta}")
    print(f"📍 FILTRO APLICADO: Cultura '{cultura}' em '{cidade}'")
    print("="*60)
    
    # 1. Busca Técnica (Com Filtro)
    contexto_tecnico = buscar_conhecimento_tecnico(pergunta, cultura)
    
    # 2. Busca Numérica
    dados_zarc = buscar_dados_zarc(cidade, cultura)
    
    resposta = f"""
    --- 🚜 RESPOSTA OFICIAL ---
    
    {dados_zarc}
    
    🧠 O QUE DIZ O MANUAL TÉCNICO DA {cultura.upper()}:
    {contexto_tecnico}S
    """
    return resposta

if __name__ == "__main__":
    # Teste Corrigido
    resp = agente_consultor(
        "Como evitar doenças fúngicas e qual o melhor solo?", 
        "Rio Verde", 
        "Soja"
    )
    print(resp)