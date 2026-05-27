import streamlit as st
import json
import os

st.set_page_config(page_title="Cold Drive", layout="wide")

# ESTILO
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background-color:#0e1117;color:white;}
[data-testid="stSidebar"]{background-color:#111;}
h1,h2,h3,h4,h5,h6,p,label{color:white !important;}
.stTextInput input{background-color:#1c1c1c;color:white;border-radius:8px;}
.stButton button{
    background-color:#e50914;
    color:white;
    border-radius:12px;
    min-height:55px;
    width:100%;
    border:none;
    font-size:16px;
    font-weight:bold;
}
.stButton button:hover{background-color:#b20710;}
</style>
""", unsafe_allow_html=True)

ARQ_USUARIOS = "usuarios.json"


def carregar_dados(arq, padrao):
    try:
        if os.path.exists(arq):
            with open(arq, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo:
                    return json.loads(conteudo)
        return padrao
    except:
        return padrao


def salvar_dados(arq, dados):
    with open(arq, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def arquivo_robos(usuario):
    return f"robos_{usuario}.json"


def arquivo_historico(usuario):
    return f"historico_{usuario}.json"


if "usuarios" not in st.session_state:
    st.session_state.usuarios = carregar_dados(ARQ_USUARIOS, {})

if "robos" not in st.session_state:
    st.session_state.robos = {}

if "historico" not in st.session_state:
    st.session_state.historico = []

if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""


def carregar_usuario(usuario):
    st.session_state.robos = carregar_dados(arquivo_robos(usuario), {})
    st.session_state.historico = carregar_dados(arquivo_historico(usuario), [])


def cadastrar_usuario(usuario, senha):
    if not usuario.strip() or not senha.strip():
        return False

    if usuario in st.session_state.usuarios:
        return False

    st.session_state.usuarios[usuario] = senha
    salvar_dados(ARQ_USUARIOS, st.session_state.usuarios)

    salvar_dados(arquivo_robos(usuario), {})
    salvar_dados(arquivo_historico(usuario), [])

    return True


def fazer_login(usuario, senha):
    if usuario in st.session_state.usuarios:
        if st.session_state.usuarios[usuario] == senha:
            st.session_state.usuario_atual = usuario
            carregar_usuario(usuario)
            return True
    return False


def logout():
    st.session_state.usuario_atual = ""
    st.session_state.robos = {}
    st.session_state.historico = []


def cadastrar_robo(nome):
    usuario = st.session_state.usuario_atual

    if not nome.strip():
        return False

    if nome in st.session_state.robos:
        return False

    st.session_state.robos[nome] = "Parado"
    st.session_state.historico.append(f"🤖 Robô {nome} cadastrado")

    salvar_dados(arquivo_robos(usuario), st.session_state.robos)
    salvar_dados(arquivo_historico(usuario), st.session_state.historico)

    return True


def controlar_robo(nome, acao):
    usuario = st.session_state.usuario_atual

    st.session_state.robos[nome] = acao
    st.session_state.historico.append(f"🤖 {nome} → {acao}")

    salvar_dados(arquivo_robos(usuario), st.session_state.robos)
    salvar_dados(arquivo_historico(usuario), st.session_state.historico)


def excluir_robo(nome):
    usuario = st.session_state.usuario_atual

    if nome in st.session_state.robos:
        del st.session_state.robos[nome]
        st.session_state.historico.append(f"🗑 Robô {nome} excluído")

        salvar_dados(arquivo_robos(usuario), st.session_state.robos)
        salvar_dados(arquivo_historico(usuario), st.session_state.historico)


# LOGIN
if st.session_state.pagina == "login":

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            "<h1 style='text-align:center;color:#e50914;'>❄️ Cold Drive</h1>",
            unsafe_allow_html=True
        )

        st.write("**Já possui cadastro? Faça seu login:**")

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if fazer_login(usuario, senha):
                st.session_state.pagina = "dashboard"
                st.rerun()
            else:
                st.error("Login inválido")

        st.divider()

        st.write("Não tem conta ainda?")

        if st.button("Criar conta"):
            st.session_state.pagina = "cadastro"
            st.rerun()


# CADASTRO
elif st.session_state.pagina == "cadastro":

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            "<h1 style='text-align:center;color:#e50914;'>Cadastro</h1>",
            unsafe_allow_html=True
        )

        usuario = st.text_input("Novo usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if cadastrar_usuario(usuario, senha):
                st.success("Conta criada com sucesso!")
            else:
                st.error("Usuário já existe ou campos vazios")

        if st.button("Voltar"):
            st.session_state.pagina = "login"
            st.rerun()


# DASHBOARD
elif st.session_state.pagina == "dashboard":

    usuario = st.session_state.usuario_atual
    carregar_usuario(usuario)

    st.sidebar.markdown("## ❄️ Cold Drive")
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {usuario}")

    menu = st.sidebar.radio("Menu", ["🏠 Início", "🤖 Robôs", "📡 Comunicação"])

    if st.sidebar.button("Sair"):
        logout()
        st.session_state.pagina = "login"
        st.rerun()

    if menu == "🏠 Início":
        st.markdown(
            "<h1 style='color:#e50914;'>❄️ Cold Drive</h1>",
            unsafe_allow_html=True
        )
        st.subheader(f"Bem-vindo, {usuario}")
        st.write("Sistema de controle de robôs via rede local.")

    elif menu == "🤖 Robôs":

        st.title("🎮 Manual de Controle")

        nome = st.text_input("Nome do robô")

        if st.button("➕ Adicionar Robô"):
            if cadastrar_robo(nome):
                st.success("Robô cadastrado!")
                st.rerun()
            else:
                st.error("Nome inválido ou robô já existe")

        st.divider()

        if len(st.session_state.robos) == 0:
            st.info("Nenhum robô cadastrado")

        else:
            for n, estado in st.session_state.robos.items():

                st.markdown(f"## 🤖 {n}")
                st.write(f"Estado: **{estado}**")

                st.markdown("### 🎮 Controle Manual")

                esp1, frente, esp2 = st.columns([1, 1, 1])

                with frente:
                    if st.button("⬆️ W", key=f"frente_{usuario}_{n}"):
                        controlar_robo(n, "Andando para frente")
                        st.rerun()

                esquerda, re, direita = st.columns(3)

                with esquerda:
                    if st.button("⬅️ A", key=f"esquerda_{usuario}_{n}"):
                        controlar_robo(n, "Virando à esquerda")
                        st.rerun()

                with re:
                    if st.button("⬇️ S", key=f"re_{usuario}_{n}"):
                        controlar_robo(n, "Andando para trás")
                        st.rerun()

                with direita:
                    if st.button("➡️ D", key=f"direita_{usuario}_{n}"):
                        controlar_robo(n, "Virando à direita")
                        st.rerun()

                st.markdown("### ⚙️ Ações")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    if st.button("🟢 Ligar", key=f"ligar_{usuario}_{n}"):
                        controlar_robo(n, "Ligado")
                        st.rerun()

                with col2:
                    if st.button("🟡 Parar", key=f"parar_{usuario}_{n}"):
                        controlar_robo(n, "Parado")
                        st.rerun()

                with col3:
                    if st.button("⛔ OFF", key=f"desligar_{usuario}_{n}"):
                        controlar_robo(n, "Desligado")
                        st.rerun()

                with col4:
                    if st.button("🗑 Excluir", key=f"excluir_{usuario}_{n}"):
                        excluir_robo(n)
                        st.rerun()

                st.divider()

    elif menu == "📡 Comunicação":

        st.title("📡 Histórico")

        if st.button("🗑 Limpar histórico"):
            st.session_state.historico = []
            salvar_dados(arquivo_historico(usuario), st.session_state.historico)
            st.rerun()

        if len(st.session_state.historico) == 0:
            st.info("Nenhuma comunicação registrada")

        else:
            for msg in reversed(st.session_state.historico):
                st.write(f"📨 {msg}")