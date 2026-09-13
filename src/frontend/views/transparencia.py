"""Explicação clara do modelo de apoio à decisão processual."""
import streamlit as st

from components.preferencias import perfil


def _estilo():
    st.markdown(
        """
        <style>
        .stApp { background:#22252d; color:#f5f5f7; }
        [data-testid="stHeader"] { background:transparent; }
        [data-testid="stAppDeployButton"], [data-testid="stMainMenu"] { display:none!important; }
        .stMainBlockContainer { max-width:1120px; padding-top:48px; padding-bottom:48px; }
        [data-testid="stSidebar"] { background:#1b1e25; border-right:1px solid #363a45; }
        h1 { font-size:32px!important; letter-spacing:-.8px; }
        .marca { font-size:30px; font-weight:600; letter-spacing:2px; margin-bottom:36px; }
        .marca span { color:#ffb133; }.perfil { display:flex; align-items:center; gap:12px; margin-bottom:30px; }
        .avatar { width:44px; height:44px; border-radius:12px; background:#ffb133; color:#22252d; display:flex; align-items:center; justify-content:center; font-weight:700; }
        .perfil-nome { font-size:15px; font-weight:600; }.perfil-empresa { color:#a5aab7; font-size:13px; margin-top:3px; }
        [data-testid="stSidebar"] .stButton button { color:#c5c9d2; border:1px solid transparent; background:transparent; justify-content:flex-start; padding:12px 16px; }
        [data-testid="stSidebar"] .stButton button:hover { color:#ffb133; background:#ffb13312; border-color:#ffb13335; }
        div[class*="st-key-nav_processos"] [data-testid="stButton"] button,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button { display:flex!important; justify-content:flex-start!important; gap:10px; text-align:left!important; }
        div[class*="st-key-nav_processos"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_historico"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button > div,
        div[class*="st-key-nav_configuracoes"] [data-testid="stButton"] button > div { flex:0 0 auto!important; width:auto!important; }
        div[class*="st-key-nav_transparencia"] [data-testid="stButton"] button { color:#ffb133; background:#ffb13318; border-color:#ffb13345; }
        .hero { background:linear-gradient(120deg,#292d36,#2d3037); border:1px solid #3b404c; border-radius:14px; padding:28px 30px; margin:12px 0 30px; }
        .hero-label, .flow-label { color:#ffb133; font-size:11px; font-weight:600; letter-spacing:1.2px; }.hero h2 { margin:9px 0 10px; font-size:22px; }.hero p { max-width:800px; color:#c5c9d2; font-size:15px; line-height:1.65; margin:0; }
        .section-title { margin:30px 0 6px; font-size:20px; font-weight:600; }.section-copy { color:#a5aab7; line-height:1.6; margin:0 0 18px; }
        .flow-card, .decision-card { height:100%; background:#292d36; border:1px solid #3b404c; border-radius:12px; padding:20px; }.flow-number { color:#ffb133; font-size:13px; font-weight:700; letter-spacing:1px; }.flow-card h3, .decision-card h3 { margin:10px 0 8px; font-size:16px; }.flow-card p, .decision-card p { margin:0; color:#b9bec9; font-size:13px; line-height:1.6; }
        .formula { margin:22px 0; padding:17px 20px; border:1px solid #ffb13345; border-radius:10px; background:#ffb1330d; color:#e4c98e; font-size:15px; line-height:1.55; }.formula strong { color:#ffb133; }
        .decision-card.low { border-top:3px solid #70b99b; }.decision-card.medium { border-top:3px solid #d5a84b; }.decision-card.high { border-top:3px solid #d76d67; }.decision-card small { display:block; color:#a5aab7; text-transform:uppercase; letter-spacing:1px; font-size:10px; }
        .notice { margin-top:28px; background:#252932; border-left:3px solid #ffb133; border-radius:8px; padding:18px 20px; color:#c5c9d2; font-size:13px; line-height:1.65; }.notice strong { color:#f5f5f7; }
        @media(max-width:720px) { .hero { padding:22px; }.stMainBlockContainer { padding-top:30px; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sidebar():
    nome_perfil, empresa_perfil = perfil()
    with st.sidebar:
        st.markdown(
            f'''<div class="marca">ENTER<span>■</span></div><div class="perfil"><div class="avatar">YK</div><div><div class="perfil-nome">{nome_perfil}</div><div class="perfil-empresa">{empresa_perfil}</div></div></div>''',
            unsafe_allow_html=True,
        )
        if st.button("Processos", icon=":material/folder_open:", key="nav_processos", use_container_width=True):
            from views.processos import render_processos
            st.switch_page(st.Page(render_processos, default=True))
        if st.button("Histórico", icon=":material/history:", key="nav_historico", use_container_width=True):
            from views.historico import render_historico
            st.switch_page(st.Page(render_historico, url_path="historico"))
        st.button("Transparência", icon=":material/visibility:", key="nav_transparencia", use_container_width=True)
        if st.button("Configurações", icon=":material/settings:", key="nav_configuracoes", use_container_width=True):
            from views.configuracoes import render_configuracoes
            st.switch_page(st.Page(render_configuracoes, url_path="configuracoes"))
        st.divider()
        if st.button("Sair da conta", use_container_width=True):
            st.session_state.clear()
            st.rerun()


def render_transparencia():
    st.set_page_config(page_title="Transparência | Enter", layout="wide", initial_sidebar_state="expanded")
    _estilo()
    _sidebar()

    st.title("Transparência")
    st.caption("Como a plataforma transforma dados do processo em apoio à decisão.")
    st.markdown(
        '''<section class="hero"><div class="hero-label">MODELO PREDITIVO DE APOIO À DECISÃO</div><h2>Uma recomendação explicável para cada processo</h2><p>A plataforma estima a probabilidade de derrota caso a estratégia seja manter a defesa. A partir dessa estimativa e do valor da causa, ela sugere uma ação e parâmetros para uma eventual negociação.</p></section>''',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">Como a recomendação é formada</div><p class="section-copy">Cada novo processo é avaliado individualmente. O modelo não reutiliza uma recomendação de outro caso.</p>', unsafe_allow_html=True)
    etapas = [
        ("01", "Leitura do caso", "São considerados os dados do processo, como assunto, UF, valor da causa e a disponibilidade dos documentos de subsídio."),
        ("02", "Probabilidade individual", "O modelo estima a chance de derrota se a estratégia adotada for a defesa, com base em padrões aprendidos a partir da base histórica."),
        ("03", "Política decisória", "A probabilidade é comparada a limiares previamente otimizados para classificar o risco e orientar a ação mais adequada."),
        ("04", "Impacto econômico", "A estimativa de risco é combinada ao valor potencial do caso e ao custo operacional para apoiar a definição de uma negociação."),
    ]
    for col, (numero, titulo, texto) in zip(st.columns(4), etapas):
        col.markdown(f'<div class="flow-card"><div class="flow-number">ETAPA {numero}</div><h3>{titulo}</h3><p>{texto}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Como o risco orienta a ação</div><p class="section-copy">Os limiares são definidos previamente para manter uma política de decisão consistente em toda a carteira.</p>', unsafe_allow_html=True)
    decisoes = [
        ("low", "Risco baixo", "A probabilidade individual fica abaixo do limiar otimizado.", "Recomendação: manter a defesa."),
        ("medium", "Risco moderado", "A probabilidade supera o limiar otimizado, mas não alcança a faixa de maior risco.", "Recomendação: avaliar acordo moderado."),
        ("high", "Risco alto", "A probabilidade alcança a faixa de maior risco definida pela política.", "Recomendação: priorizar acordo imediato."),
    ]
    for col, (classe, titulo, criterio, acao) in zip(st.columns(3), decisoes):
        col.markdown(f'<div class="decision-card {classe}"><small>Classificação</small><h3>{titulo}</h3><p>{criterio}</p><p style="margin-top:12px;color:#f5f5f7">{acao}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Como os valores de negociação são sugeridos</div>', unsafe_allow_html=True)
    st.markdown('<div class="formula"><strong>Custo esperado da defesa</strong> = probabilidade de derrota × perda estimada + custo operacional do caso</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-copy">Com esse custo esperado, a plataforma sugere um valor inicial para iniciar a negociação e um teto máximo para orientar até onde ela pode avançar. Esses valores buscam dar previsibilidade à conversa, sem substituir a análise do caso concreto.</p>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><strong>Revisão profissional é indispensável.</strong> A recomendação é um apoio à decisão e não uma garantia de resultado judicial. O advogado responsável deve avaliar as provas, teses, particularidades do processo e a estratégia do cliente antes de definir defesa, acordo ou valores de negociação.</div>', unsafe_allow_html=True)
