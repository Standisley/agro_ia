import os
import requests
import time

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
KNOWLEDGE_PATH = os.path.join(BASE_PATH, "data", "knowledge")

os.makedirs(KNOWLEDGE_PATH, exist_ok=True)

# --- BIBLIOTECA TÉCNICA (Links Oficiais Embrapa) ---
# Selecionamos Manuais, Circulares Técnicas e Sistemas de Produção.
MANUAIS = {
    # --- DOCUMENTOS GERAIS ---
    "zarc_metodologia.pdf": "https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/seguro-rural/documentos/metodologia-zarc.pdf",
    
    # --- GRÃOS (Embrapa Soja / Milho e Sorgo) ---
    "soja_manejo.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1123868/1/Soja-no-Brasil.pdf",
    "milho_tecnologia.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1090099/1/Circular-Tecnica-127.pdf",
    
    # --- FRUTAS (Embrapa Mandioca e Fruticultura / Citros) ---
    # Nota: Links diretos para circulares técnicas
    "banana_irrigacao.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1126600/1/CirTec120.pdf",
    "laranja_citricultura.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/883460/1/Citrus-plantio.pdf", # Exemplo genérico
    "abacaxi_producao.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1123400/1/Circular-Tecnica-130.pdf",
    "maracuja_tecnologia.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/661853/1/CiTec_66.pdf",
    
    # --- HORTALIÇAS (Embrapa Hortaliças) ---
    "tomate_doencas.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/111867/1/ct-56.pdf",
    "alface_cultivo_organico.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/777649/1/SistProd1.pdf",
    "cenoura_producao.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1144439/1/Cartilha-Cenoura-Cerrado.pdf",
    "pimentao_cultivo.pdf": "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/111863/1/ct-52.pdf"
}

def baixar_pdfs():
    print(f"--- 📚 Iniciando Download da Biblioteca Técnica (11 Arquivos) ---")
    print(f"Destino: {KNOWLEDGE_PATH}\n")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    sucessos = 0
    falhas = 0

    for nome_arquivo, url in MANUAIS.items():
        caminho_final = os.path.join(KNOWLEDGE_PATH, nome_arquivo)
        
        # Se o arquivo já existe e tem tamanho > 0, pula
        if os.path.exists(caminho_final) and os.path.getsize(caminho_final) > 0:
            print(f"⚠️  [Já Existe] {nome_arquivo}")
            sucessos += 1
            continue
            
        print(f"⬇️  Baixando: {nome_arquivo}...")
        
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            
            if response.status_code == 200:
                with open(caminho_final, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"   ✅ Download concluído.")
                sucessos += 1
            else:
                print(f"   ❌ Erro {response.status_code} no link da Embrapa.")
                falhas += 1
                
        except Exception as e:
            print(f"   ❌ Falha de conexão: {e}")
            falhas += 1
        
        # Pausa de 1 segundo para não sobrecarregar o servidor da Embrapa
        time.sleep(1)

    print("\n" + "="*40)
    print(f"RELATÓRIO FINAL:")
    print(f"✅ Arquivos prontos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"📂 Verifique a pasta: {KNOWLEDGE_PATH}")
    print("="*40)

if __name__ == "__main__":
    baixar_pdfs()