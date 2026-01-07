import pandas as pd
import os
import random

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
RAW_PATH = os.path.join(BASE_PATH, "data", "raw")

# Cria a pasta data/raw se ela não existir
os.makedirs(RAW_PATH, exist_ok=True)

def ingest_zarc_data():
    """
    Função principal de Ingestão de Dados (Versão Ampliada 2.0).
    Simula ZARC para Grãos, Frutas Variadas e Hortaliças.
    """
    print(f"--- Iniciando Ingestão ZARC (10 Culturas) em: {RAW_PATH} ---")

    # 1. Definição do Escopo
    municipios = [
        {"cod_ibge": 5218805, "nome": "Rio Verde", "uf": "GO"},
        {"cod_ibge": 5211909, "nome": "Jataí", "uf": "GO"},
        {"cod_ibge": 5206206, "nome": "Cristalina", "uf": "GO"}, # Capital da Cenoura/Alho
        {"cod_ibge": 5213103, "nome": "Mineiros", "uf": "GO"},
        {"cod_ibge": 5205109, "nome": "Catalão", "uf": "GO"}
    ]
    
    # Lista expandida: 2 Grãos + 4 Frutas + 4 Hortaliças
    culturas = [
        # Grãos
        "Soja", "Milho",
        # Frutas
        "Banana", "Laranja", "Abacaxi", "Maracujá",
        # Hortaliças
        "Tomate Mesa", "Alface", "Cenoura", "Pimentão"
    ]
    
    # Solos
    tipos_solo = ["AD1", "AD2", "AD3"]

    dados_zarc = []

    print("Gerando matriz de riscos diversificada...")
    
    for mun in municipios:
        for cultura in culturas:
            for solo in tipos_solo:
                for decendio in range(1, 37):
                    
                    # --- Lógica de Negócio (Simulação) ---
                    mes = (decendio - 1) // 3 + 1
                    risco = 20 # Risco base (ótimo)
                    
                    # --- GRUPO 1: GRÃOS ---
                    if cultura == "Soja":
                        if 4 <= mes <= 9: risco = 40 # Seca
                        elif solo == "AD1": risco = 30
                    
                    elif cultura == "Milho":
                        if mes > 3 and mes < 10: risco = 30
                    
                    # --- GRUPO 2: FRUTAS ---
                    elif cultura == "Banana":
                        # Sensível a frio (Jun-Ago)
                        if 6 <= mes <= 8: risco = 30 
                    
                    elif cultura == "Laranja":
                        # Florada Set/Out precisa de água
                        if mes == 9 or mes == 10: risco = 30
                    
                    elif cultura == "Abacaxi":
                        # Muito rústico, mas plantio na seca extrema atrasa ciclo
                        if mes == 7 or mes == 8: risco = 30
                        # Solo AD1 (Areia) é bom para abacaxi (não apodrece raiz), mantém risco baixo
                    
                    elif cultura == "Maracujá":
                        # Risco alto de doenças fúngicas em chuvas extremas (Jan/Fev)
                        # E precisa de água na seca (Ago/Set)
                        if mes <= 2: risco = 30
                        if mes == 8 or mes == 9: risco = 30

                    # --- GRUPO 3: HORTALIÇAS ---
                    elif cultura == "Tomate Mesa":
                        # Odeia chuva excessiva
                        if mes <= 2 or mes == 12: risco = 40 
                        else: risco = 20
                            
                    elif cultura == "Alface":
                        # Odeia calor/sol forte e chuva na cabeça
                        if mes == 1 or mes == 12: risco = 30
                    
                    elif cultura == "Cenoura":
                        # Raiz: Se o solo encharcar, apodrece.
                        # Verão chuvoso em GO (Dez-Fev) é péssimo (Risco Alto)
                        if mes == 12 or mes <= 2: 
                            risco = 40
                        # Inverno seco (com irrigação) é a safra de ouro em Cristalina
                        elif 5 <= mes <= 8:
                            risco = 20
                    
                    elif cultura == "Pimentão":
                        # Parente do tomate, mas exige calor constante.
                        # Frio de Junho/Julho trava o desenvolvimento
                        if 6 <= mes <= 7: risco = 30
                        # Chuva excessiva também mancha fruto
                        if mes == 1: risco = 30
                    
                    # --- Fim das Lógicas ---

                    # Variação aleatória
                    if random.random() > 0.96: risco += 10
                    
                    # Formatação
                    nota_risco = str(risco)
                    if risco > 40: nota_risco = "INAPTO"

                    dados_zarc.append({
                        "uf": mun["uf"],
                        "municipio": mun["nome"],
                        "cod_ibge": mun["cod_ibge"],
                        "cultura": cultura,
                        "safra": "2025/2026",
                        "solo": solo,
                        "decendio": decendio,
                        "risco": nota_risco
                    })

    # 3. Salvamento
    df = pd.DataFrame(dados_zarc)
    arquivo_destino = os.path.join(RAW_PATH, "zarc_goias_bruto.csv")
    
    df.to_csv(arquivo_destino, index=False, sep=";", encoding="utf-8")
    
    print(f"Sucesso! Arquivo salvo: {arquivo_destino}")
    print(f"Novas culturas adicionadas: Abacaxi, Maracujá, Cenoura, Pimentão.")
    print(f"Total de registros: {len(df)}")

if __name__ == "__main__":
    ingest_zarc_data()