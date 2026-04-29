import streamlit as st
from streamlit_autorefresh import st_autorefresh
from supabase import create_client

SUPABASE_URL = "https://gypxqraeewtafxhzlpht.supabase.co"
SUPABASE_KEY = "sb_publishable_IKOTWRfZpboaZVQwTBj6mw_WY79VMYx"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="VRO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "selected_votes" not in st.session_state:
    st.session_state.selected_votes = []

if "show_new_postit" not in st.session_state:
    st.session_state.show_new_postit = False

if "logado" not in st.session_state:
    st.session_state.logado = False

if "evento" not in st.session_state:
    st.session_state.evento = ""

if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""


def current_event():
    return st.session_state.evento


def get_ideas():
    res = (
        supabase.table("ideas")
        .select("*")
        .eq("evento", current_event())
        .order("id", desc=True)
        .execute()
    )
    return res.data or []


def get_vote_counts():
    res = (
        supabase.table("votes")
        .select("idea_id")
        .eq("evento", current_event())
        .execute()
    )
    rows = res.data or []

    counts = {}
    for row in rows:
        idea_id = row["idea_id"]
        counts[idea_id] = counts.get(idea_id, 0) + 1

    return counts


def toggle_vote(idea_id):
    current = st.session_state.selected_votes.copy()

    if idea_id in current:
        current.remove(idea_id)
    else:
        if len(current) < 3:
            current.append(idea_id)

    st.session_state.selected_votes = current


def save_votes(user_name):
    supabase.table("votes") \
        .delete() \
        .eq("evento", current_event()) \
        .eq("user_name", user_name) \
        .execute()

    rows = []
    for idea_id in st.session_state.selected_votes:
        rows.append({
            "evento": current_event(),
            "user_name": user_name,
            "idea_id": idea_id
        })

    if rows:
        supabase.table("votes").insert(rows).execute()


def user_has_voted(user_name):
    res = (
        supabase.table("votes")
        .select("id")
        .eq("evento", current_event())
        .eq("user_name", user_name)
        .execute()
    )
    return len(res.data or []) > 0


def get_top_map(ideas, vote_counts):
    ranking_ids = sorted(
        [idea["id"] for idea in ideas],
        key=lambda x: vote_counts.get(x, 0),
        reverse=True
    )
    return {iid: pos for pos, iid in enumerate(ranking_ids[:3], start=1)}


def get_card_bg(i, selected=False):
    palette = ["#FFF7D6", "#EAF6E3", "#E9F2FB", "#FFF1E6", "#F7ECF5"]
    if selected:
        return "#DFF7E8"
    return palette[i % len(palette)]


def get_border(top_pos=None, selected=False):
    if selected:
        return "#22c55e"
    if top_pos == 1:
        return "#eab308"
    if top_pos == 2:
        return "#6366f1"
    if top_pos == 3:
        return "#ec4899"
    return "#dbe4ee"


def badge_text(top_pos=None, selected=False):
    badges = []

    if selected:
        badges.append("Votado")
    else:
        if top_pos == 1:
            badges.append("Top 1")
        elif top_pos == 2:
            badges.append("Top 2")
        elif top_pos == 3:
            badges.append("Top 3")

    return " • ".join(badges)


st.markdown("""
<style>
header {visibility: hidden; height: 0px !important;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.stApp {
    background: #f4f7fb;
    margin-top: -18px;
}

.block-container {
    max-width: 100% !important;
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #0f172a !important;
}

.hero {
    background: #f4f7fb;
    padding: 18px 8px 8px 8px;
    margin-bottom: 0.8rem;
}

.main-title {
    text-align: center;
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.1rem;
}

.sub-title {
    text-align: center;
    color: #475569;
    font-size: 0.98rem;
    margin-bottom: 0.2rem;
}

label, .stTextInput label, .stTextArea label {
    color: #0f172a !important;
    font-weight: 700;
}

.stTextInput input,
.stTextArea textarea {
    color: #0f172a !important;
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 14px !important;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.9);
    border-radius: 14px 14px 0 0;
    border: 1px solid rgba(15,23,42,0.06);
    padding: 10px 16px;
    color: #0f172a !important;
    font-weight: 600;
}

.helper {
    color: #475569;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.rank-box {
    background: #ffffff !important;
    border: 1px solid rgba(15,23,42,0.10);
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
    color: #0f172a !important;
    font-weight: 600;
}

.rank-box * {
    color: #0f172a !important;
}

.card-shell {
    border-radius: 20px;
    padding: 14px;
    min-height: 320px;
    margin-bottom: 10px;
    box-shadow: 0 8px 20px rgba(15,23,42,0.07);
}

.card-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.card-chip {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.73rem;
    font-weight: 700;
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(15,23,42,0.06);
    color: #0f172a !important;
    white-space: nowrap;
}

.card-title {
    font-size: 1.08rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 2px;
}

.section-label {
    font-size: 0.8rem;
    font-weight: 800;
    color: #334155;
    margin-top: 10px;
    margin-bottom: 2px;
}

.section-text {
    font-size: 0.92rem;
    color: #0f172a;
    line-height: 1.38;
}

.stButton > button {
    width: 100% !important;
    min-height: 46px !important;
    height: 46px !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    background-color: #0f172a !important;
    color: #ffffff !important;
    border: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label span,
div[data-testid="stCheckbox"] p {
    color: #0f172a !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

div[data-testid="stAlert"], div[data-testid="stAlert"] * {
    color: #0f172a !important;
}

div[data-testid="stForm"] {
    background: #FFF7D6 !important;
    border: 2px solid #eab308 !important;
    border-radius: 22px !important;
    padding: 20px !important;
    box-shadow: 0 8px 20px rgba(15,23,42,0.08) !important;
    margin-bottom: 18px !important;
}

div[data-testid="stForm"] h3 {
    color: #0f172a !important;
    font-weight: 800;
}

div[data-testid="stForm"] textarea {
    background-color: #FFF7D6 !important;
    color: #0f172a !important;
    border: 1px solid #eab308 !important;
    border-radius: 14px !important;
}

@media (max-width: 768px) {
    .card-shell {
        min-height: 280px;
        padding: 12px;
    }
    .main-title {
        font-size: 1.7rem;
    }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <div class="main-title">VRO - Value Realization Office</div>
    <div class="sub-title">Idea Prioritization Board</div>
</div>
""", unsafe_allow_html=True)


if not st.session_state.logado:
    st.markdown("### Acesso")

    login_nome = st.text_input("Seu nome")
    login_evento = st.text_input("Senha / código do evento", type="password")

    if st.button("Entrar", use_container_width=True):
        if login_nome.strip() and login_evento.strip():
            st.session_state.logado = True
            st.session_state.nome_usuario = login_nome.strip()
            st.session_state.evento = login_evento.strip()
            st.session_state.selected_votes = []
            st.rerun()
        else:
            st.error("Digite seu nome e a senha do evento.")

    st.stop()


name = st.session_state.nome_usuario

st.caption(f"Evento atual: {st.session_state.evento}")

tab1, tab2, tab3, tab4 = st.tabs(["Ideias", "Votação", "Resultado", "Projetar"])

modo_telao = st.checkbox("Modo Projetar: atualizar automaticamente")

if modo_telao:
    st_autorefresh(interval=3000, key="auto_refresh")


def show_card(idea, idx, vote_count=0, selected=False, top_pos=None):
    idea_id = idea["id"]
    problema = idea.get("problema", "")
    impacto = idea.get("impacto", "")
    solucao = idea.get("solucao", "")
    monetizado = idea.get("monetizado", "")

    bg = get_card_bg(idx, selected=selected)
    border = get_border(top_pos=top_pos, selected=selected)
    badge = badge_text(top_pos=top_pos, selected=selected)

    badge_html = f'<span class="card-chip">{badge}</span>' if badge else ""

    card_html = f"""<div class="card-shell" style="background:{bg}; border:2px solid {border};">
<div class="card-meta">
<div>{badge_html}</div>
<div><span class="card-chip">{vote_count} voto(s)</span></div>
</div>
<div class="card-title">Ideia {idea_id}</div>
<div class="section-label">1 - Problema Inicial</div>
<div class="section-text">{problema}</div>
<div class="section-label">2 - Impactados pelo problema</div>
<div class="section-text">{impacto}</div>
<div class="section-label">3 - Hipótese de Solução</div>
<div class="section-text">{solucao}</div>
<div class="section-label">4 - Resultado/Impacto [Monetizado]</div>
<div class="section-text">{monetizado}</div>
</div>"""

    st.markdown(card_html, unsafe_allow_html=True)


with tab1:
    st.markdown(
        '<div class="helper">Clique em “Adicionar post-it” para criar uma nova ideia.</div>',
        unsafe_allow_html=True
    )

    if st.button("+ Adicionar post-it", use_container_width=True):
        st.session_state.show_new_postit = True

    if st.session_state.show_new_postit:
        with st.form("novo_postit_form", clear_on_submit=True):
            st.markdown("### Novo post-it")

            problema = st.text_area("1 - Problema Inicial", key="novo_problema")
            impacto = st.text_area("2 - Impactados pelo problema", key="novo_impacto")
            solucao = st.text_area("3 - Hipótese de Solução", key="nova_solucao")
            monetizado = st.text_area("4 - Resultado/Impacto [Monetizado]", key="novo_monetizado")

            salvar = st.form_submit_button("Salvar post-it", use_container_width=True)

            if salvar:
                if problema and impacto and solucao and monetizado:
                    supabase.table("ideas").insert({
                        "evento": current_event(),
                        "autor": name,
                        "problema": problema,
                        "impacto": impacto,
                        "solucao": solucao,
                        "monetizado": monetizado
                    }).execute()

                    st.session_state.show_new_postit = False
                    st.success("Post-it salvo com sucesso.")
                    st.rerun()
                else:
                    st.error("Preencha os 4 campos do post-it.")

        if st.button("Cancelar", use_container_width=True):
            st.session_state.show_new_postit = False
            st.rerun()

    ideias = get_ideas()
    vote_counts = get_vote_counts()

    st.markdown("### Mural")
    if not ideias:
        st.info("Ainda não há ideias cadastradas.")
    else:
        top_map = get_top_map(ideias, vote_counts)
        cols = st.columns(3)

        for i, idea in enumerate(ideias):
            idea_id = idea["id"]
            with cols[i % 3]:
                show_card(
                    idea=idea,
                    idx=i,
                    vote_count=vote_counts.get(idea_id, 0),
                    selected=False,
                    top_pos=top_map.get(idea_id)
                )


with tab2:
    st.markdown(
        '<div class="helper">Selecione até 3 ideias marcando a opção abaixo de cada card.</div>',
        unsafe_allow_html=True
    )

    ideias = get_ideas()
    vote_counts = get_vote_counts()

    if not ideias:
        st.info("Ainda não há ideias para votar.")
    else:
        ja_votou = user_has_voted(name)

        top_map = get_top_map(ideias, vote_counts)
        cols = st.columns(3)

        for i, idea in enumerate(ideias):
            idea_id = idea["id"]
            is_selected = idea_id in st.session_state.selected_votes

            with cols[i % 3]:
                show_card(
                    idea=idea,
                    idx=i,
                    vote_count=vote_counts.get(idea_id, 0),
                    selected=is_selected,
                    top_pos=top_map.get(idea_id)
                )

                novo_valor = st.checkbox(
                    "Votar",
                    value=is_selected,
                    key=f"check_{idea_id}",
                    disabled=ja_votou or (not is_selected and len(st.session_state.selected_votes) >= 3)
                )

                if not ja_votou:
                    if novo_valor and idea_id not in st.session_state.selected_votes:
                        toggle_vote(idea_id)
                        st.rerun()

                    if not novo_valor and idea_id in st.session_state.selected_votes:
                        toggle_vote(idea_id)
                        st.rerun()

        st.markdown("---")

        if len(st.session_state.selected_votes) == 3:
            st.info("Você atingiu o limite máximo de 3 ideias.")

        if ja_votou:
            st.success("Seus votos já foram computados.")
            st.button("Votos confirmados", use_container_width=True, disabled=True)
        else:
            if st.button(
                "Confirmar votos",
                use_container_width=True,
                disabled=(len(st.session_state.selected_votes) == 0)
            ):
                save_votes(name)
                st.success("Votos registrados com sucesso.")
                st.rerun()


with tab3:
    ideias = get_ideas()
    vote_counts = get_vote_counts()

    if not ideias:
        st.info("Ainda não há ideias cadastradas.")
    elif not vote_counts:
        st.info("Ainda não há votos.")
    else:
        ranking = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)

        st.markdown(
            '<h3 style="color:#0f172a; font-weight:800; margin-bottom:10px;">Ideias em destaque</h3>',
            unsafe_allow_html=True
        )
        
        for idx, (idea_id, votos) in enumerate(ranking[:3], start=1):
            idea = next((i for i in ideias if i["id"] == idea_id), None)
            if idea:
                with cols[(idx - 1) % 3]:
                    show_card(
                        idea=idea,
                        idx=idx - 1,
                        vote_count=votos,
                        selected=False,
                        top_pos=idx
                    )
        
        st.markdown(
            '<h3 style="color:#0f172a; font-weight:800;">Ranking</h3>',
            unsafe_allow_html=True
        )

        for pos, (idea_id, votos) in enumerate(ranking, start=1):
            idea = next((i for i in ideias if i["id"] == idea_id), None)
            if idea:
                medal = "1º" if pos == 1 else "2º" if pos == 2 else "3º" if pos == 3 else f"{pos}º"
                st.markdown(
                    f'<div class="rank-box"><b>{medal}</b> Ideia {idea["id"]} — {idea.get("solucao", "")} <span style="float:right;"><b>{votos}</b> voto(s)</span></div>',
                    unsafe_allow_html=True
                )


with tab4:
    st.markdown("### Modo Projetar")

    ideias = get_ideas()
    vote_counts = get_vote_counts()

    if not ideias:
        st.info("Ainda não há ideias cadastradas.")
    else:
        top_map = get_top_map(ideias, vote_counts)
        cols = st.columns(3)

        for i, idea in enumerate(ideias):
            idea_id = idea["id"]
            with cols[i % 3]:
                show_card(
                    idea=idea,
                    idx=i,
                    vote_count=vote_counts.get(idea_id, 0),
                    selected=False,
                    top_pos=top_map.get(idea_id)
                )
