import os

# --- CONFIGURAÇÃO ---
BASE_PATH = r"C:\Users\standisley.costa\Documents\Repos\Standis\agricultura_ia"
KNOWLEDGE_PATH = os.path.join(BASE_PATH, "data", "knowledge")

os.makedirs(KNOWLEDGE_PATH, exist_ok=True)

# --- CONTEÚDO TÉCNICO (SIMULANDO OS MANUAIS) ---
CONTEUDO_AGRONOMICO = {
    "soja_manual_tecnico.txt": """
    CULTURA: SOJA (Glycine max)
    
    1. EXIGÊNCIAS CLIMÁTICAS
    A soja é sensível ao fotoperíodo. A temperatura ideal para crescimento é entre 20°C e 30°C.
    Temperaturas abaixo de 10°C paralisam o crescimento. Acima de 40°C causam abortamento de flores.
    Necessidade hídrica: 450 a 800 mm por ciclo. O déficit hídrico é crítico na floração e enchimento de grãos.
    
    2. SOLOS E ADUBAÇÃO
    Prefere solos profundos, drenados e com pH entre 5.5 e 6.5 (correção com calcário é essencial em Goiás).
    Solos arenosos (AD1) exigem maior parcelamento de potássio para evitar lixiviação.
    
    3. PRINCIPAIS DOENÇAS EM GOIÁS
    - Ferrugem Asiática (Phakopsora pachyrhizi): Requer monitoramento constante. Controle químico preventivo.
    - Antracnose: Favorecida por alta umidade e temperaturas quentes.
    - Mofo Branco: Comum em áreas de altitude (ex: Cristalina) e alta tecnologia.
    """,

    "milho_safrinha_manual.txt": """
    CULTURA: MILHO SAFRINHA (Zea mays)
    
    1. JANELA DE PLANTIO
    Em Goiás, o ideal é plantar logo após a colheita da soja, até 20 de fevereiro.
    Plantios em março aumentam drasticamente o risco de perda por seca em maio/junho ou geada (no sul de GO).
    
    2. DENSIDADE
    Recomenda-se entre 50.000 a 60.000 plantas por hectare para safrinha, menor que no verão devido à menor oferta de água.
    
    3. PRAGAS ALVO
    - Cigarrinha do Milho (Dalbulus maidis): Vetor dos enfezamentos. Controle deve começar no tratamento de sementes.
    - Lagarta-do-cartucho: Controle com milho Bt e refúgio estruturado.
    """,

    "tomate_mesa_manual.txt": """
    CULTURA: TOMATE DE MESA
    
    1. CLIMA
    O tomateiro exige termoperiodicidade (diferença entre dia e noite).
    Umidade excessiva favorece doenças. Em Goiás, o plantio de verão (período chuvoso) exige estufas ou controle fitossanitário rigoroso.
    A melhor época a céu aberto é o período seco (irrigado), de abril a agosto.
    
    2. DOENÇAS CRÍTICAS
    - Requeima (Phytophthora infestans): Destrutiva em clima frio e úmido.
    - Vira-cabeça: Transmitido por tripes. Controle do vetor é crucial.
    
    3. NUTRIÇÃO
    Exigente em Cálcio (para evitar Fundo Preto) e Boro.
    """,

    "cenoura_cerrado_manual.txt": """
    CULTURA: CENOURA (Daucus carota)
    
    1. SISTEMAS DE PRODUÇÃO NO CERRADO
    Cristalina/GO é o maior polo. Ocorre o ano todo, mas exige cultivares de "verão" (resistentes a queima-das-folhas) e "inverno".
    
    2. SOLO
    Não tolera solos compactados ou encharcados, que causam deformação da raiz (bifurcação).
    O preparo de solo profundo (subsolagem) é obrigatório.
    
    3. NEMATOIDES
    A cultura é muito sensível a nematoides de galha (Meloidogyne spp.). Rotação com gramíneas (milho/sorgo) é recomendada.
    """,

    "banana_irrigada.txt": """
    CULTURA: BANANA
    
    1. NECESSIDADE HÍDRICA
    Planta de alto consumo (transpiração elevada). No Cerrado, a irrigação é obrigatória.
    Déficit hídrico causa "engasgamento" do cacho e frutos pequenos.
    
    2. MAL-DO-PANAMÁ
    Doença de solo (Fungo Fusarium). Não tem cura química.
    Controle: Uso de variedades resistentes e mudas sadias. Evitar trânsito de máquinas de áreas contaminadas.
    """,

    "laranja_citros.txt": """
    CULTURA: LARANJA
    
    1. FLORADA
    A florada principal em GO ocorre com as primeiras chuvas (setembro/outubro).
    Estresse hídrico severo nesse ponto causa abortamento floral.
    
    2. GREENING (HLB)
    A pior doença da citricultura atual. Transmitida pelo psilídeo.
    Não tem cura. O controle é erradicar plantas doentes e controlar o inseto vetor regionalmente.
    """,

    "abacaxi_perola.txt": """
    CULTURA: ABACAXI PÉROLA
    
    1. INDUÇÃO FLORAL
    O florescimento natural ocorre no inverno (dias curtos e frios).
    Para colheita programada, usa-se indução artificial (Ethephon/Carbureto) a partir do 8º mês.
    
    2. FUSARIOSE
    Principal doença. Causa exsudação de goma no fruto.
    Controle: Mudas sadias e controle da broca-do-fruto (que abre porta para o fungo).
    """,
    
    "maracuja_azedo.txt": """
    CULTURA: MARACUJÁ AZEDO
    
    1. POLINIZAÇÃO
    Depende exclusivamente das abelhas mamangavas (Xylocopa).
    O uso de inseticidas deve ser feito apenas no final da tarde para não matar os polinizadores.
    Sem mamangava, não há fruto (ou frutos ficam ocos).
    
    2. VIDA ÚTIL
    Devido a doenças de solo (Fusarium/Bacterioses), o pomar comercial dura de 1 a 2 anos no máximo.
    """,
    
    "alface_hidroponia_campo.txt": """
    CULTURA: ALFACE
    
    1. TIPBURN (QUEIMA DA BORDA)
    Distúrbio fisiológico por falta de Cálcio nas folhas jovens.
    Causado por crescimento muito rápido em dias quentes ou baixa transpiração em dias nublados.
    
    2. PINGO-DE-OURO
    Doença viral (Vírus do Vira-Cabeça) comum em regiões quentes. Controle de tripes é essencial.
    """,
    
    "pimentao_campo_aberto.txt": """
    CULTURA: PIMENTÃO
    
    1. QUEIMA DE FRUTOS (SOL)
    Frutos expostos ao sol forte de Goiás sofrem escaldadura.
    É necessário ter bom enfolhamento da planta para proteger os frutos.
    
    2. EXCESSO DE NITROGÊNIO
    Adubação nitrogenada excessiva provoca muito crescimento vegetativo e pouca produção de flores/frutos.
    """
}

def gerar_conhecimento_sintetico():
    print(f"--- 🏭 Gerando Manuais Técnicos (Fallback) ---")
    print(f"Destino: {KNOWLEDGE_PATH}\n")
    
    sucessos = 0
    
    for nome_arquivo, texto in CONTEUDO_AGRONOMICO.items():
        caminho_final = os.path.join(KNOWLEDGE_PATH, nome_arquivo)
        
        try:
            with open(caminho_final, 'w', encoding='utf-8') as f:
                # Remove espaços extras do início das linhas para ficar bonito
                texto_limpo = "\n".join([line.strip() for line in texto.split("\n")])
                f.write(texto_limpo)
            
            print(f"✅ Gerado: {nome_arquivo}")
            sucessos += 1
        except Exception as e:
            print(f"❌ Erro ao salvar {nome_arquivo}: {e}")

    print("\n" + "="*40)
    print(f"STATUS FINAL: {sucessos} manuais gerados com sucesso.")
    print("O sistema RAG (Milvus) poderá ler esses arquivos normalmente.")
    print("="*40)

if __name__ == "__main__":
    gerar_conhecimento_sintetico()