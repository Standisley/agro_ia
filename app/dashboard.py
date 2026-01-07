import streamlit as st
import pandas as pd
import os
import chromadb
from chromadb.utils import embedding_functions
import joblib
from datetime import timedelta, datetime
from groq import Groq
import re

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="AgroIA - Diagnóstico Inteligente", page_icon="🌾", layout="wide")

# --- AJUSTE DE CAMINHOS ---
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARQUET_FILE = os.path.join(BASE_PATH, "data", "processed", "dataset_gold_mvp.parquet")
MODEL_PATH = os.path.join(BASE_PATH, "models", "modelo_produtividade.joblib")
DB_PATH = os.path.join(BASE_PATH, "data", "chroma_db")

# --- DADOS ECONÔMICOS E TÉCNICOS ---
PRECO_VENDA = {
    "Soja": 130.00, "Milho": 60.00, "Banana": 40.00, "Laranja": 35.00, 
    "Tomate Mesa": 75.00, "Cenoura": 55.00, "Pimentão": 45.00, 
    "Abacaxi": 5.00, "Maracujá": 50.00, "Alface": 2.00
}

FATOR_CUSTO = {
    "Soja": 1.0, "Milho": 1.0, "Banana": 1.2, "Laranja": 1.2, 
    "Tomate Mesa": 2.0, "Cenoura": 1.5, "Pimentão": 1.8, 
    "Abacaxi": 1.5, "Maracujá": 1.3, "Alface": 1.3 
}

FATOR_PRODUTIVIDADE = {
    "Soja": 1.0, "Milho": 1.2, "Banana": 35.0, "Laranja": 25.0, 
    "Tomate Mesa": 80.0, "Cenoura": 60.0, "Pimentão": 50.0, 
    "Abacaxi": 250.0, "Maracujá": 25.0, "Alface": 350.0
}

PERDA_PADRAO = {
    "Soja": 0.05, "Milho": 0.05, "Banana": 0.15, "Laranja": 0.10, 
    "Tomate Mesa": 0.25, "Cenoura": 0.20, "Pimentão": 0.20, 
    "Abacaxi": 0.10, "Maracujá": 0.15, "Alface": 0.30
}

CICLO_MEDIO_DIAS = {
    "Soja": 120, "Milho": 135, "Banana": 365, "Laranja": 365, 
    "Tomate Mesa": 100, "Cenoura": 100, "Pimentão": 110,
    "Abacaxi": 540, "Maracujá": 240, "Alface": 45
}

TIPO_CULTURA = {
    "Soja": "Ciclo Curto (Anual)",
    "Milho": "Ciclo Curto (Anual)",
    "Banana": "Perene (Produção contínua, início 1 ano)",
    "Laranja": "Perene (Árvore - 1ª Safra Comercial em 3 a 4 anos)",
    "Tomate Mesa": "Ciclo Curto (Hortaliça)",
    "Cenoura": "Ciclo Curto (Hortaliça)",
    "Pimentão": "Ciclo Curto (Hortaliça)",
    "Abacaxi": "Ciclo Longo (18 meses)",
    "Maracujá": "Semi-Perene (1 a 2 anos)",
    "Alface": "Ciclo Curtíssimo"
}

# --- FUNÇÕES ---
def get_decendio(data):
    mes = data.month
    dia = data.day
    parte_mes = 0
    if dia <= 10: parte_mes = 1
    elif dia <= 20: parte_mes = 2
    else: parte_mes = 3
    return (mes - 1) * 3 + parte_mes

@st.cache_data
def carregar_dados():
    if not os.path.exists(PARQUET_FILE): return None
    df = pd.read_parquet(PARQUET_FILE)
    mapa = {'chuva_acumulada_decendio': 'chuva_media_mm', 'temp': 'temp_media_c'}
    df.rename(columns=mapa, inplace=True)
    if 'decendio' in df.columns: df.rename(columns={'decendio': 'periodo'}, inplace=True)
    elif 'periodo' not in df.columns: df['periodo'] = 1 
    return df

@st.cache_resource
def carregar_ml():
    if os.path.exists(MODEL_PATH): return joblib.load(MODEL_PATH)
    return None

@st.cache_resource
def carregar_chroma():
    try:
        # Tenta corrigir problema do SQLite em algumas nuvens
        __import__('pysqlite3')
        import sys
        sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
    except ImportError: pass
    
    try:
        if not os.path.exists(DB_PATH): return None
        client = chromadb.PersistentClient(path=DB_PATH)
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        return client.get_collection(name="manual_tecnico_agricola", embedding_function=emb_fn)
    except: return None

# --- LLAMA 3.3 (AGORA COM RAG CONECTADO) ---
def consultar_llama_online(cultura, cidade, lucro, risco, clima_texto, area_calc, texto_tecnico):
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key: return "⚠️ Erro: Chave de API da Groq não configurada."

    client = Groq(api_key=api_key)

    info_ciclo = TIPO_CULTURA.get(cultura, "Ciclo Padrão")
    
    chuva_match = re.search(r'\((\d+)mm\)', clima_texto)
    mm_chuva = int(chuva_match.group(1)) if chuva_match else 0
    
    alerta_irrigacao = ""
    if mm_chuva < 30:
        alerta_irrigacao = "ALERTA CRÍTICO: Baixa chuva. Avise que SEM IRRIGAÇÃO o plantio é inviável."

    # Prompt Turbinado com o Knowledge Base
    prompt_usuario = f"""
    Aja como um Agrônomo Sênior. Analise este cenário:
    
    DADOS DO PROJETO:
    - Município: {cidade}
    - Cultura: {cultura} ({info_ciclo})
    - Área: {area_calc:.1f} ha
    - Clima Hoje: {clima_texto}
    - {alerta_irrigacao}

    TRECHO DO MANUAL TÉCNICO (Use como referência extra):
    "{texto_tecnico[:1000]}"  # Limitamos a 1000 caracteres para não estourar

    SUA MISSÃO (Responda em 3 frases curtas):
    1. Valide o clima/irrigação para a data.
    2. Explique o tempo de retorno (se for perene) e cite algo do manual se for útil.
    3. Dê o veredito (Lucro Projetado: R$ {lucro:,.0f}).
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt_usuario}],
            temperature=0.4, 
            max_tokens=400,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"IA Indisponível."

# --- CÁLCULO INTELIGENTE ---
def recomendar_cultura(df, modelo, cidade, area_input, orcamento_max, ignorar_lista, data_plantio, usar_todo_orcamento):
    resultados = []
    df_cidade = df[df['municipio'] == cidade]
    culturas_existentes = df_cidade['cultura'].unique().tolist()
    decendio_alvo = get_decendio(data_plantio)
    
    for cultura in culturas_existentes:
        if cultura in ignorar_lista: continue
        
        dados_cultura = df_cidade[df_cidade['cultura'] == cultura]
        linha_decendio = dados_cultura[dados_cultura['periodo'] == decendio_alvo]
        
        if linha_decendio.empty:
            risco = 100
            custo_base_ha = 2000
            obs = "Fora da Janela"
            prod_score, solo_val, chuva, temp = 0, 1, 0, 30
            clima_status = "Desconhecido"
        else:
            dado = linha_decendio.iloc[0]
            risco = dado['risco_numerico']
            custo_base_ha = dado['custo_ha_est']
            solo_val = 2
            chuva = dado.get('chuva_media_mm', 0)
            temp = dado.get('temp_media_c', 25)
            
            if chuva < 15: clima_status = f"🌵 Seco ({chuva:.0f}mm)"
            elif chuva > 80: clima_status = f"🌧️ Chuva Intensa ({chuva:.0f}mm)"
            else: clima_status = f"💧 Ideal ({chuva:.0f}mm)"

            SENSIVEIS = ["Tomate Mesa", "Alface", "Pimentão", "Cenoura"]
            if cultura in SENSIVEIS and chuva > 80:
                risco = max(risco, 50)
                obs = "⛔ Excesso Chuva"
            elif risco >= 40: obs = "⛔ Risco Alto"
            elif risco >= 20: obs = "⚠️ Risco Médio"
            else: obs = "✅ Favorável"
                
            prod_score = 50
            if modelo:
                prod_score = modelo.predict([[risco, chuva, temp, custo_base_ha, solo_val]])[0]

        custo_por_ha = custo_base_ha * FATOR_CUSTO.get(cultura, 1.0)
        
        if usar_todo_orcamento:
            area_real = orcamento_max / custo_por_ha
            if area_real < 0.1: area_real = 0.1
        else:
            area_real = area_input

        custo_total = custo_por_ha * area_real
        prod_bruta = prod_score * FATOR_PRODUTIVIDADE.get(cultura, 1.0) * area_real
        perda_pct = PERDA_PADRAO.get(cultura, 0.10)
        
        if risco >= 50: perda_pct = 0.95
        elif risco > 30: perda_pct = 0.50
            
        receita = prod_bruta * (1 - perda_pct) * PRECO_VENDA.get(cultura, 0)
        lucro = receita - custo_total
        roi = (lucro / custo_total) * 100 if custo_total > 0 else 0
        
        status = "Viável"
        if lucro < 0: status = "Prejuízo"
        elif not usar_todo_orcamento and custo_total > orcamento_max: 
            status = "Orçamento Insuficiente"

        fator_seguranca = 1.0
        if risco > 20: fator_seguranca = 0.5
        if risco > 40: fator_seguranca = 0.1
        score = lucro * fator_seguranca
        
        dias = CICLO_MEDIO_DIAS.get(cultura, 120)
        colheita = (data_plantio + timedelta(days=dias)).strftime("%d/%m/%Y")

        resultados.append({
            "Cultura": cultura, "Risco": risco, "Custo": custo_total,
            "Lucro": lucro, "Score": score, "ROI": roi, "Status": status,
            "Obs": obs, "Clima": clima_status, "Colheita": colheita, 
            "Area_Calc": area_real
        })
    
    return pd.DataFrame(resultados), culturas_existentes

# --- CARD UI ---
def card_metrica(titulo, valor, cor="#000000"):
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #e9ecef; margin-bottom: 5px;">
        <p style="font-size: 12px; color: #6c757d; margin-bottom: 0px;">{titulo}</p>
        <p style="font-size: 20px; font-weight: bold; color: {cor}; margin: 0px;">{valor}</p>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN ---
def main():
    st.title(f"AgroIA - Diagnóstico Inteligente")
    
    df = carregar_dados()
    modelo = carregar_ml()
    chroma = carregar_chroma() # Aqui carregamos o banco de vetores
    
    if df is None: st.error("Erro: Dados não encontrados."); st.stop()

    with st.sidebar:
        st.header("📍 Configuração")
        cidade = st.selectbox("Município:", df['municipio'].unique())
        culturas = df[df['municipio'] == cidade]['cultura'].unique()
        data_plantio = st.date_input("Data Plantio:", datetime.today())
        
        st.divider()
        st.write("💰 **Defina o Orçamento:**")
        
        perfil = st.radio("Selecione:", ["🟢 Pequeno (Até 20k)", "🟡 Médio (Até 100k)", "🔴 Alto (Até 500k)", "✏️ Outro"], label_visibility="collapsed")
        if "Pequeno" in perfil: orcamento = 20000.0
        elif "Médio" in perfil: orcamento = 100000.0
        elif "Alto" in perfil: orcamento = 500000.0
        else: orcamento = st.number_input("Valor R$:", value=50000.0)

        usar_todo_orcamento = st.checkbox("Usar todo o orçamento (Maximizar Área)", value=True)
        
        if not usar_todo_orcamento:
            area = st.number_input("Área Fixa (ha):", value=1.0)
        else:
            area = 1.0 
            st.info(f"O sistema vai calcular quantos hectares você consegue plantar com R$ {orcamento:,.0f}")

        st.divider()
        ignorar = st.multiselect("Ignorar Culturas:", options=culturas)
        btn = st.button("ANALISAR AGORA", type="primary")

    if btn:
        with st.spinner("Simulando cenários..."):
            df_res, _ = recomendar_cultura(df, modelo, cidade, area, orcamento, ignorar, data_plantio, usar_todo_orcamento)
            
            if df_res.empty: st.error("Sem dados.")
            else:
                df_bom = df_res[df_res['Status'] == "Viável"].sort_values('Score', ascending=False)
                df_ruim = df_res[df_res['Status'] != "Viável"].sort_values('Lucro', ascending=False)
                
                if not df_bom.empty:
                    campeao = df_bom.iloc[0]
                    area_calculada = campeao['Area_Calc']
                    
                    st.markdown(f"""
                    <div style="padding: 15px; background-color: #d4edda; border-radius: 10px; margin-bottom: 20px;">
                        <h3 style="color: #155724; margin:0;">🏆 Melhor Opção: {campeao['Cultura'].upper()} ({area_calculada:.1f} ha)</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2, c3, c4, c5 = st.columns(5)
                    with c1: card_metrica("Lucro Líquido", f"R$ {campeao['Lucro']:,.2f}", "#198754")
                    with c2: card_metrica("ROI", f"{campeao['ROI']:.0f}%", "#0d6efd")
                    with c3: card_metrica("Investimento", f"R$ {campeao['Custo']:,.2f}", "#dc3545")
                    with c4: card_metrica("Colheita", campeao['Colheita'])
                    with c5: card_metrica("Condição", campeao['Clima'], "#fd7e14")
                    
                    # --- BUSCA NO KNOWLEDGE BASE (RAG) ---
                    texto_tecnico = ""
                    if chroma:
                        try:
                            # Busca específica sobre a cultura campeã
                            query = f"Manejo tecnico plantio {campeao['Cultura']}"
                            results = chroma.query(query_texts=[query], n_results=1)
                            if results['documents']:
                                texto_tecnico = results['documents'][0][0]
                        except Exception as e:
                            print(f"Erro no Chroma: {e}")
                    
                    # Passamos o texto recuperado para a IA
                    parecer = consultar_llama_online(
                        campeao['Cultura'], 
                        cidade, 
                        campeao['Lucro'], 
                        campeao['Risco'], 
                        campeao['Clima'], 
                        area_calculada,
                        texto_tecnico # <--- AGORA SIM!
                    )
                    
                    st.markdown(f"""
                    <div style="background-color: #e2e3e5; padding: 15px; border-radius: 8px; margin-top: 10px;">
                        <b>🧠 Parecer Técnico:</b> {parecer}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.divider()
                    st.subheader("📊 Tabela Detalhada")
                    
                    df_view = df_bom[['Cultura', 'Area_Calc', 'Lucro', 'Custo', 'Risco', 'Obs', 'Clima']].copy()
                    
                    df_view['Lucro'] = df_view['Lucro'].apply(lambda x: f"R$ {x:,.2f}")
                    df_view['Custo'] = df_view['Custo'].apply(lambda x: f"R$ {x:,.2f}")
                    df_view['Area_Calc'] = df_view['Area_Calc'].apply(lambda x: f"{x:.1f} ha")
                    
                    df_view.rename(columns={'Area_Calc': 'Área Sugerida'}, inplace=True)
                    
                    st.dataframe(df_view, hide_index=True, use_container_width=True)
                else:
                    st.warning(f"Nenhuma cultura viável para o orçamento.")

                if not df_ruim.empty:
                    st.divider()
                    st.caption("Opções Descartadas")
                    st.dataframe(df_ruim[['Cultura', 'Lucro', 'Status', 'Obs']], hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()