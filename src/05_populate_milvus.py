import os
from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer
from tqdm import tqdm # Barra de progresso

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
KNOWLEDGE_PATH = os.path.join(BASE_PATH, "data", "knowledge")
DB_PATH = os.path.join(BASE_PATH, "data", "milvus_agro.db") # O arquivo do banco

# --- 1. INICIALIZAÇÃO ---
print("--- 🧠 Iniciando Banco Vetorial (Milvus Lite) ---")

# Inicializa o Milvus em um arquivo local (Ideal para MVP)
client = MilvusClient(DB_PATH)

# Nome da Coleção (Tabela)
COLLECTION_NAME = "manual_tecnico_agricola"

# Se já existe, apaga para recriar limpo (Reset do MVP)
if client.has_collection(collection_name=COLLECTION_NAME):
    client.drop_collection(collection_name=COLLECTION_NAME)

# Cria a coleção configurada para vetores de tamanho 384 (Padrão do modelo MiniLM)
client.create_collection(
    collection_name=COLLECTION_NAME,
    dimension=384,
    metric_type="COSINE", # Métrica para encontrar similaridade
    auto_id=True
)

print(f"✅ Coleção '{COLLECTION_NAME}' criada com sucesso!")

# --- 2. CARREGAR MODELO DE EMBEDDING ---
print("📥 Carregando modelo de IA (sentence-transformers)...")
# Modelo pequeno, rápido e gratuito para rodar no seu PC
model = SentenceTransformer('all-MiniLM-L6-v2') 

# --- 3. PROCESSAR ARQUIVOS E INSERIR ---
arquivos = [f for f in os.listdir(KNOWLEDGE_PATH) if f.endswith('.txt')]
dados_para_inserir = []

print(f"📖 Lendo {len(arquivos)} manuais sintéticos...")

for arquivo in arquivos:
    caminho = os.path.join(KNOWLEDGE_PATH, arquivo)
    
    with open(caminho, 'r', encoding='utf-8') as f:
        texto_completo = f.read()
    
    # Estratégia de Chunking (Fatiamento):
    # Vamos quebrar o texto por parágrafos duplos para ter contextos melhores
    paragrafos = texto_completo.split('\n\n')
    
    for i, paragrafo in enumerate(paragrafos):
        paragrafo = paragrafo.strip()
        if len(paragrafo) < 20: continue # Pula parágrafos muito curtos
        
        # A MÁGICA: Transforma texto em vetor
        vetor = model.encode(paragrafo).tolist()
        
        # Prepara o pacote de dados
        dados_para_inserir.append({
            "vector": vetor,
            "texto": paragrafo,
            "fonte": arquivo,
            "topico": arquivo.replace("_manual.txt", "").replace(".txt", "")
        })

# --- 4. INSERÇÃO NO BANCO ---
print(f"🚀 Inserindo {len(dados_para_inserir)} fragmentos de conhecimento no Milvus...")

res = client.insert(
    collection_name=COLLECTION_NAME,
    data=dados_para_inserir
)

print(f"✅ Sucesso! Inseridos: {res['insert_count']} vetores.")
print(f"💾 Banco salvo em: {DB_PATH}")
print("O sistema agora 'sabe' ler e recomendar com base técnica.")