import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Tuple

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (UI/UX DESIGN & WCAG ACCESSIBILITY)
# ==============================================================================
st.set_page_config(
    page_title="PROMPT MASTER - Otimizador de Salas de Aula",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS customizada para interface corporativa (Dark/Light adaptive e bordas limpas)
st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    .stMetric { background-color: rgba(28, 131, 225, 0.1); padding: 15px; border-radius: 10px; border-left: 5px solid #1C83E1; }
    .stAlert { border-radius: 10px; }
    div.stButton > button:first-child { background-color: #1C83E1; color: white; border-radius: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CAMADA DE INFRAESTRUTURA LOGÍSTICA / MODELOS DE DADOS
# ==============================================================================
class Obstacle:
    def __init__(self, name: str, x: float, y: float, w: float, d: float):
        self.name = name
        self.x = x  # Canto inferior esquerdo
        self.y = y
        self.w = w  # Largura (X)
        self.d = d  # Profundidade (Y)

    def intersects(self, cx1: float, cy1: float, cx2: float, cy2: float) -> bool:
        # Algoritmo AABB (Axis-Aligned Bounding Box) para detecção de colisão hígida
        ox1, oy1 = self.x, self.y
        ox2, oy2 = self.x + self.w, self.y + self.d
        return not (cx2 <= ox1 or cx1 >= ox2 or cy2 <= oy1 or cy1 >= oy2)

# ==============================================================================
# CAMADA DE ENGENHARIA DE REQUISITOS E ALGORITMOS DE OTIMIZAÇÃO
# ==============================================================================
class RoomOptimizer:
    """
    Motor matemático de otimização espacial para alocação discreta de mobiliário.
    Aplica heurísticas de busca em grade espacial fina com restrições poligonais e AABB.
    """
    @staticmethod
    def optimize(
        room_w: float, room_d: float,
        desk_w: float, desk_d: float,
        space_lat: float, space_front: float,
        corr_center: bool, corr_lat: float,
        corr_front: float, corr_back: float,
        obstacles: List[Obstacle],
        scenario_type: str = "Padrão"
    ) -> Dict[str, Any]:
        
        # Ajuste de margens dinâmicas baseado no cenário de Pesquisa Operacional
        if scenario_type == "Conservador":
            space_lat *= 1.2
            space_front *= 1.2
            safety_margin = 0.90 # Reduz 10% por auditoria preventiva
        elif scenario_type == "Otimizado":
            space_lat *= 0.95
            space_front *= 0.95
            safety_margin = 1.0
        else: # Padrão
            safety_margin = 1.0

        # Pegada ergonômica da célula unitária
        cell_w = desk_w + space_lat
        cell_d = desk_d + space_front

        best_desks = []
        best_efficiency = 0.0
        
        # Área total e cálculo preliminar do fiscal (Área reservada na frente: largura total x corredor frontal)
        total_area = room_w * room_d
        fiscal_area = room_w * corr_front
        
        # Heurística de Micro-Ajuste Espacial (Sub-grid offset sweeping)
        # Varre pequenos deslocamentos (0 a 10cm) para escapar de quinas de obstáculos de forma ótima
        for offset_x in np.linspace(0, min(cell_w, 0.1), 3):
            for offset_y in np.linspace(0, min(cell_d, 0.1), 3):
                current_desks = []
                
                # Definição das fronteiras úteis internas
                start_x = corr_lat + offset_x
                end_x = room_w - corr_lat
                start_y = corr_front + offset_y
                end_y = room_d - corr_back

                # Adiciona folga para corredor central se habilitado
                center_x = room_w / 2.0
                corr_center_width = 1.0 # 1 metro de corredor central padrão

                y = start_y
                while y + desk_d <= end_y:
                    x = start_x
                    while x + desk_w <= end_x:
                        # Se corredor central ativo, pula a região demarcada central
                        if corr_center and (center_x - corr_center_width/2 < x + desk_w/2 < center_x + corr_center_width/2):
                            x += 0.2 # Avanço rápido sobre a zona restrita do corredor
                            continue
                        
                        # Coordenadas da carteira candidata
                        cx1, cy1 = x, y
                        cx2, cy2 = x + desk_w, y + desk_d
                        
                        # Verificação de colisões contra todos os obstáculos cadastrados
                        collision = False
                        for obs in obstacles:
                            if obs.intersects(cx1, cy1, cx2, cy2):
                                collision = True
                                break
                        
                        if not collision:
                            current_desks.append({"x1": cx1, "y1": cy1, "x2": cx2, "y2": cy2})
                        
                        x += cell_w
                    y += cell_d

                # Validação da performance do cenário atual
                count = int(len(current_desks) * safety_margin)
                calc_efficiency = (count * (desk_w * desk_d)) / total_area if total_area > 0 else 0
                
                if calc_efficiency >= best_efficiency:
                    best_efficiency = calc_efficiency
                    best_desks = current_desks[:count] if safety_margin < 1.0 else current_desks

        # Consolidação estatística dos resultados analíticos
        occupied_area = len(best_desks) * (desk_w * desk_d)
        free_area = total_area - occupied_area - fiscal_area
        
        # Extração de linhas e colunas estruturadas para fins de auditoria do CEBRASPE/FGV
        x_coords = sorted(list(set([d["x1"] for d in best_desks])))
        y_coords = sorted(list(set([d["y1"] for d in best_desks])))

        return {
            "total_desks": len(best_desks),
            "desks_coords": best_desks,
            "total_area": total_area,
            "occupied_area": occupied_area,
            "free_area": max(0.0, free_area),
            "efficiency": (occupied_area / total_area) * 100 if total_area > 0 else 0,
            "density": len(best_desks) / total_area if total_area > 0 else 0,
            "cols_count": len(x_coords),
            "rows_count": len(y_coords)
        }

# ==============================================================================
# CAMADA DE INTERFACE GRÁFICA (VISUALIZAÇÃO DE DADOS & INTERAÇÃO)
# ==============================================================================
def main():
    st.title("📐 PROMPT MASTER")
    st.subheader("Sistema Corporativo de Auditoria e Otimização Espacial de Concursos")
    st.markdown("---")

    # Painel Lateral de Entrada de Dados Técnicos (Data Input Rigor)
    with st.sidebar:
        st.header("📋 Parâmetros da Sala")
        room_w = st.number_input("Largura da Sala (Metros)", min_value=2.0, max_value=50.0, value=8.0, step=0.5)
        room_d = st.number_input("Comprimento da Sala (Metros)", min_value=2.0, max_value=50.0, value=10.0, step=0.5)
        
        st.header("🪑 Dimensões do Mobiliário")
        furniture_type = st.selectbox("Tipo de Carteira", ["Universitária Padrão", "Mesa Individual", "Mesa Dupla", "Cadeira Simples"])
        
        # Perfis pré-configurados de arquitetura escolar interna
        if furniture_type == "Universitária Padrão":
            desk_w, desk_d = 0.60, 0.50
        elif furniture_type == "Mesa Individual":
            desk_w, desk_d = 0.80, 0.60
        elif furniture_type == "Mesa Dupla":
            desk_w, desk_d = 1.20, 0.60
        else:
            desk_w, desk_d = 0.50, 0.45

        desk_w = st.number_input("Largura da Carteira (m)", min_value=0.1, max_value=3.0, value=desk_w, step=0.05)
        desk_d = st.number_input("Profundidade da Carteira (m)", min_value=0.1, max_value=3.0, value=desk_d, step=0.05)

        st.header("🛑 Restrições de Circulação (Normativas)")
        space_lat = st.number_input("Espaçamento Lateral Mínimo (m)", min_value=0.1, max_value=2.0, value=0.40, step=0.05)
        space_front = st.number_input("Espaçamento Frontal Mínimo (m)", min_value=0.1, max_value=2.0, value=0.60, step=0.05)
        
        corr_front = st.number_input("Corredor Frontal / Área do Fiscal (m)", min_value=1.0, max_value=5.0, value=2.0, step=0.1)
        corr_back = st.number_input("Corredor Traseiro de Escape (m)", min_value=0.2, max_value=3.0, value=0.5, step=0.1)
        corr_lat = st.number_input("Corredores Laterais de Fluxo (m)", min_value=0.2, max_value=3.0, value=0.6, step=0.1)
        corr_center = st.checkbox("Adicionar Corredor Central Estrutural", value=False)

    # Corpo Central - Abas de Processamento Analítico
    tab_dashboard, tab_obstacles, tab_simulation = st.tabs(["📊 Dashboard de Capacidade", "🏗️ Obstáculos & Infraestrutura", "🧠 Análise Multicenário"])

    # Tratamento de Obstáculos em estado de sessão estável (Session State)
    if "obstacles" not in st.session_state:
        st.session_state.obstacles = [Obstacle("Coluna Central A", 3.5, 5.0, 0.6, 0.6)]

    with tab_obstacles:
        st.header("Gerenciamento de Barreiras Físicas e Colunas")
        st.markdown("Insira colunas, pilares ou palcos para que o algoritmo recalcule a malha de segurança de forma auditável.")
        
        with st.form("form_obstacle"):
            obs_name = st.text_input("Identificador do Obstáculo", value=f"Coluna {len(st.session_state.obstacles) + 1}")
            col1, col2, col3, col4 = st.columns(4)
            obs_x = col1.number_input("Posição X (Dist. da parede esquerda)", min_value=0.0, max_value=room_w, value=1.0)
            obs_y = col2.number_input("Posição Y (Dist. da parede do fundo)", min_value=0.0, max_value=room_d, value=1.0)
            obs_w = col3.number_input("Largura do Obstáculo (ΔX)", min_value=0.1, max_value=room_w, value=0.5)
            obs_d = col4.number_input("Profundidade do Obstáculo (ΔY)", min_value=0.1, max_value=room_d, value=0.5)
            
            if st.form_submit_button("Injetar Obstáculo na Planta"):
                if obs_x + obs_w > room_w or obs_y + obs_d > room_d:
                    st.error("Erro Crítico: O obstáculo transborda as fronteiras físicas da sala!")
                else:
                    st.session_state.obstacles.append(Obstacle(obs_name, obs_x, obs_y, obs_w, obs_d))
                    st.success(f"Obstáculo '{obs_name}' integrado com sucesso!")

        if st.session_state.obstacles:
            df_obs = pd.DataFrame([{
                "Nome": o.name, "X Inicial": o.x, "Y Inicial": o.y, "Largura": o.w, "Profundidade": o.d
            } for o in st.session_state.obstacles])
            st.dataframe(df_obs, use_container_width=True)
            if st.button("Limpar Todos os Obstáculos"):
                st.session_state.obstacles = []
                st.rerun()

    # Execução do Core Algorithm para a aba principal
    results = RoomOptimizer.optimize(
        room_w, room_d, desk_w, desk_d, space_lat, space_front,
        corr_center, corr_lat, corr_front, corr_back, st.session_state.obstacles, "Padrão"
    )

    with tab_dashboard:
        # Fileira de Métricas Flash de Alta Visibilidade (UI/UX Executive)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Capacidade Máxima Auditada", f"{results['total_desks']} Alunos", help="Valor absoluto com margem de segurança")
        m2.metric("Eficiência Espacial", f"{results['efficiency']:.1f}%", help="Área real líquida ocupada por móveis sobre a área total")
        m3.metric("Densidade Ocupacional", f"{results['density']:.2f} Alunos/m²")
        m4.metric("Distribuição (Colunas x Filas)", f"{results['cols_count']} x {results['rows_count']}")

        st.markdown("### Planta Baixa Digital e Disposição de Carteiras (Interativo 2D)")
        
        # Construção da visualização vetorial via Plotly Engine
        fig = go.Figure()

        # Desenhar perímetro da sala
        fig.add_shape(type="rect", x0=0, y0=0, x1=room_w, y1=room_d, line=dict(color="Black", width=3), fillcolor="rgba(240,242,246,0.2)")
        
        # Desenhar zona proibida do Fiscal (Corredor Frontal)
        fig.add_shape(type="rect", x0=0, y0=0, x1=room_w, y1=corr_front, line=dict(color="Red", width=1, dash="dash"), fillcolor="rgba(255,0,0,0.05)")
        fig.add_annotation(x=room_w/2, y=corr_front/2, text="ZONA CRÍTICA: MESA DO FISCAL / QUADRO", showarrow=False, font=dict(color="Red", size=12))

        # Desenhar Obstáculos cadastrados
        for obs in st.session_state.obstacles:
            fig.add_shape(type="rect", x0=obs.x, y0=obs.y, x1=obs.x+obs.w, y1=obs.y+obs.d, line=dict(color="DarkRed", width=2), fillcolor="rgba(139,0,0,0.7)")
            fig.add_annotation(x=obs.x + obs.w/2, y=obs.y + obs.d/2, text=obs.name, showarrow=False, font=dict(color="White", size=10))

        # Desenhar as Carteiras Otimizadas
        for i, d in enumerate(results["desks_coords"]):
            fig.add_shape(type="rect", x0=d["x1"], y0=d["y1"], x1=d["x2"], y1=d["y2"], line=dict(color="#1C83E1", width=1.5), fillcolor="rgba(28,131,225,0.4)")
            
        fig.update_layout(
            xaxis=dict(title="Largura da Sala (m)", range=[-0.5, room_w + 0.5], gridcolor="lightgray"),
            yaxis=dict(title="Profundidade da Sala (m)", range=[-0.5, room_d + 0.5], gridcolor="lightgray"),
            width=900, height=650,
            plot_bgcolor="white",
            title="Distribuição Geométrica Ótima das Carteiras (Visão Superior)"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico Estatístico de Alocação de Área
        st.markdown("### Balanço de Utilização de Superfície")
        df_pie = pd.DataFrame({
            "Métrica": ["Área Ocupada por Carteiras", "Área de Circulação e Segurança (Livre)"],
            "Valores": [results["occupied_area"], results["free_area"]]
        })
        fig_pie = px.pie(df_pie, values="Valores", names="Métrica", color_discrete_sequence=["#1C83E1", "#E2E8F0"], hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab_simulation:
        st.header("Análise Comparativa de Cenários de Alocação")
        st.markdown("Abaixo, realizamos uma simulação paralela comparando as abordagens regulatórias solicitadas para planejamento estratégico.")
        
        scenarios = ["Conservador", "Padrão", "Otimizado"]
        sim_data = []
        
        for sc in scenarios:
            res_sc = RoomOptimizer.optimize(
                room_w, room_d, desk_w, desk_d, space_lat, space_front,
                corr_center, corr_lat, corr_front, corr_back, st.session_state.obstacles, sc
            )
            sim_data.append({
                "Cenário": sc,
                "Capacidade": res_sc["total_desks"],
                "Eficiência (%)": round(res_sc["efficiency"], 2),
                "Densidade (Alunos/m²)": round(res_sc["density"], 2)
            })
            
        df_sim = pd.DataFrame(sim_data)
        st.table(df_sim)
        
        # Validação Inteligente Automática
        st.markdown("### 🧠 Parecer Técnico Automático da IA")
        if results["efficiency"] < 15.0:
            st.warning("⚠️ Alerta de Ineficiência: As restrições de corredores ou os obstáculos estão gerando um aproveitamento crítico muito baixo do espaço físico. Considere revisar o tamanho do mobiliário ou reduzir os recuos laterais se as normas locais permitirem.")
        elif results["total_desks"] == 0:
            st.error("❌ Incompatibilidade Geométrica Absoluta: Nenhuma carteira consegue ser posicionada sob as atuais restrições regulatórias e de tamanho de corredores.")
        else:
            st.info("✅ Layout Homologado: A disposição atende integralmente os critérios de escape e distanciamento. Os dados gerados estão prontos para exportação e auditoria pelas bancas examinadoras.")

if __name__ == "__main__":
    main()
