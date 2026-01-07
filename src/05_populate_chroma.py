import os
import chromadb
from chromadb.utils import embedding_functions

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
KNOWLEDGE_PATH = os.path.join(BASE_PATH, "data", "knowledge")
DB_PATH = os.path.join(BASE_PATH, "data", "chroma_db") # Pasta onde o banco vai ficar

print("--- 🧠 Iniciando Banco Vetorial (ChromaDB) ---")

# 1. INICIALIZAÇÃO
# Cria um banco persistente no disco (não apaga quando fecha o python)
client = chromadb.PersistentClient(path=DB_PATH)

# Função de Embedding (A IA que transforma texto em número)
# Usamos o modelo padrão 'all-MiniLM-L6-v2' que é leve e rápido
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Cria ou recupera a coleção
collection = client.get_or_create_collection(
    name="manual_tecnico_agricola",
    embedding_function=emb_fn
)

print(f"✅ Banco conectado em: {DB_PATH}")

# 2. PROCESSAR ARQUIVOS
arquivos = [f for f in os.listdir(KNOWLEDGE_PATH) if f.endswith('.txt')]
print(f"📖 Lendo {len(arquivos)} manuais sintéticos...")

ids = []
documentos = []
metadados = []

for arquivo in arquivos:
    caminho = os.path.join(KNOWLEDGE_PATH, arquivo)
    
    with open(caminho, 'r', encoding='utf-8') as f:
        texto_completo = f.read()
    
    # Fatiamento por parágrafos duplos
    paragrafos = texto_completo.split('\n\n')
    
    for i, paragrafo in enumerate(paragrafos):
        paragrafo = paragrafo.strip()
        if len(paragrafo) < 20: continue 
        
        # Prepara listas para inserção em lote (batch)
        id_unico = f"{arquivo}_{i}" # ID ex: soja_manual.txt_0
        
        ids.append(id_unico)
        documentos.append(paragrafo) # O Chroma vetoriza isso automaticamente
        metadados.append({"fonte": arquivo, "topico": arquivo.replace(".txt", "")})

# 3. INSERÇÃO NO BANCO
if documentos:
    print(f"🚀 Inserindo {len(documentos)} fragmentos de conhecimento...")
    collection.add(
        ids=ids,
        documents=documentos,
        metadatas=metadados
    )
    print(f"✅ Sucesso! Dados salvos e indexados.")
else:
    print("⚠️ Nenhum dado novo encontrado para inserir.")