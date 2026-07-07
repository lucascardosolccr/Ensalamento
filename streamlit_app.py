import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# TENTATIVA DEFENSIVA DE IMPORTAÇÃO GRÁFICA (Prevenção de quebra do servidor)
HAS_MATPLOTLIB = False
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (UI/UX DESIGN & ACCESSIBILITY)
# ==============================================================================
st.set_page_config(
    page_title="PROMPT MASTER - Otimizador de Salas",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS de nível corporativo
st.markdown("""
<style>
    .reportview-container .main .block-container { padding-top: 2rem; }
    .stMetric { background-color: rgba(28, 131, 225, 0.08); padding: 15px; border-radius: 10px; border-left: 5px solid #1C83E1; }
    .stAlert { border-radius: 10px; }
    div.stButton > button:first-child { background-color: #1C83E1; color: white; border-radius: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MODELO DE INFRAESTRUTURA LOGÍSTICA
# ==============================================================================
class Obstacle:
    def __init__(self, name: str, x: float, y: float, w: float, d: float):
        self.name = name
        self.x = x
        self.y = y
        self.w = w
        self.d = d

    def intersects(self, cx1: float, cy1: float, cx2: float, cy2: float) -> bool:
        ox1, oy1 = self.x, self.y
        ox2, oy2 = self.x + self.w, self.y + self.d
        return not (cx2 <= ox1 or cx1 >= ox2 or cy2 <= oy1 or cy1 >= oy2)

# ==============================================================================
# MOTOR MATEMÁTICO DE OTIMIZAÇÃO (PESQUISA OPERACIONAL)
# ==============================================================================
class RoomOptimizer:
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
        
        if scenario_type == "Conservador":
            space_lat *= 1.2
            space_front *= 1.2
            safety_margin = 0.90
        elif scenario_type == "Otimizado":
            space_lat *= 0.95
            space_front *= 0.95
            safety_margin = 1.0
        else:
            safety_margin = 1.0

        cell_w = desk_w + space_lat
        cell_d = desk_d + space_front

        best_desks = []
        best_efficiency = 0.0
        
        total_area = room_w * room_d
        fiscal_area = room_w * corr_front
        
        for offset_x in np.linspace(0, min(cell_w, 0.1), 3):
            for offset_y in np.linspace(0, min(cell_d, 0.1), 3):
                current_desks = []
                
                start_x = corr_lat + offset_x
                end_x = room_w - corr_lat
                start_y = corr_front + offset_y
                end_y = room_d - corr_back

                center_x = room_w / 2.0
                corr_center_width = 1.0

                y = start_y
                while y + desk_d <= end_y:
                    x = start_x
                    while x + desk_w <= end_x:
                        if corr_center and (center_x - corr_center_width/2 < x + desk_w/2 < center_x + corr_center_width/2):
                            x += 0.2
                            continue
                        
                        cx1, cy1 = x, y
                        cx2, cy2 = x + desk_w, y + desk_d
                        
                        collision = False
                        for obs in obstacles:
                            if obs.intersects(cx1, cy1, cx2, cy2):
                                collision = True
                                break
                        
                        if not collision:
                            current_desks.append({"x1": cx1, "y1": cy1, "x2": cx2, "y2": cy2})
                        
                        x += cell_w
                    y += cell_d

                count = int(len(current_desks) * safety_margin)
                calc_efficiency = (count * (desk_w * desk_d)) / total_area if total_area > 0 else 0
                
                if calc_efficiency >= best_efficiency:
                    best_efficiency = calc_efficiency
                    best_desks = current_desks[:count] if safety_margin < 1.0 else current_desks

        occupied_area = len(best_desks) * (desk_w * desk_d)
        free_area = total_area - occupied_area - fiscal_area
        
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
# INTERFACE GRÁFICA DO USUÁRIO
# ==============================================================================
def main():
    st.title("📐 PROMPT MASTER")
    st.subheader("Sistema Corporativo de Auditoria e Otimização Espacial de Concursos")
    st.markdown("---")

    with st.sidebar:
        st.header("📋 Parâmetros da Sala")
        room_w = st.number_input("Largura da Sala (Metros)", min_value=2.0, max_value=50.0, value=8.0, step=0.5)
        room_d = st.number_input("Comprimento da Sala (Metros)", min_value=2.0, max_value=50.0, value=10.0, step=0.5)
        
        st.header("🪑 Dimensões do Mobiliário")
        furniture_type = st.selectbox("Tipo de Carteira", ["Universitária Padrão", "Mesa Individual", "Mesa Dupla", "Cadeira Simples"])
        
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

        st.header("🛑 Restrições de Circulação")
        space_lat = st.number_input("Espaçamento Lateral Mínimo (m)", min_value=0.1, max_value=2.0, value=0.40, step=0.05)
        space_front = st.number_input("Espaçamento Frontal Mínimo (m)", min_value=0.1, max_value=2.0, value=0.60, step=0.05)
        
        corr_front = st.number_input("Corredor Frontal / Área do Fiscal (m)", min_value=1.0, max_value=5.0, value=2.0, step=0.1)
        corr_back = st.number_input("Corredor Traseiro de Escape (m)", min_value=0.2, max_value=3.0, value=0.5, step=0.1)
        corr_lat = st.number_input("Corredores Laterais de Fluxo (m)", min_value=0.2, max_value=3.0, value=0.6, step=0.1)
        corr_center = st.checkbox("Adicionar Corredor Central Estrutural", value=False)

    tab_dashboard, tab_obstacles, tab_simulation = st.tabs(["📊 Dashboard de Capacidade", "🏗️ Obstáculos & Infraestrutura", "🧠 Análise Multicenário"])

    if "obstacles" not in st.session_state:
        st.session_state.obstacles = [Obstacle("Coluna Central A", 3.5, 5.0, 0.6, 0.6)]

    with tab_obstacles:
        st.header("Gerenciamento de Barreiras Físicas e Colunas")
        with st.form("form_obstacle"):
            obs_name = st.text_input("Identificador do Obstáculo", value=f"Coluna {len(st.session_state.obstacles) + 1}")
            col1, col2, col3, col4 = st.columns(4)
            obs_x = col1.number_input("Posição X (Dist. da parede esquerda)", min_value=0.0, max_value=room_w, value=1.0)
            obs_y = col2.number_input("Posição Y (Dist. da parede do fundo)", min_value=0.0, max_value=room_d, value=1.0)
            obs_w = col3.number_input("Largura do Obstáculo (ΔX)", min_value=0.1, max_value=room_w, value=0.5)
            obs_d = col4.number_input("Profundidade do Obstáculo (ΔY)", min_value=0.1, max_value=room_d, value=0.5)
            
            if st.form_submit_button("Injetar Obstáculo na Planta"):
                if obs_x + obs_w > room_w or obs_y + obs_d > room_d:
                    st.error("Erro Crítico: O obstáculo transborda as fronteiras da sala!")
                else:
                    st.session_state.obstacles.append(Obstacle(obs_name, obs_x, obs_y, obs_w, obs_d))
                    st.rerun()

        if st.session_state.obstacles:
            df_obs = pd.DataFrame([{
                "Nome": o.name, "X Inicial": o.x, "Y Inicial": o.y, "Largura": o.w, "Profundidade": o.d
            } for o in st.session_state.obstacles])
            st.dataframe(df_obs, use_container_width=True)
            if st.button("Limpar Todos os Obstáculos"):
                st.session_state.obstacles = []
                st.rerun()

    results = RoomOptimizer.optimize(
        room_w, room_d, desk_w, desk_d, space_lat, space_front,
        corr_center, corr_lat, corr_front, corr_back, st.session_state.obstacles, "Padrão"
    )

    with tab_dashboard:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Capacidade Máxima Auditada", f"{results['total_desks']} Alunos")
        m2.metric("Eficiência Espacial", f"{results['efficiency']:.1f}%")
        m3.metric("Densidade Ocupacional", f"{results['density']:.2f} Alunos/m²")
        m4.metric("Distribuição (Colunas x Filas)", f"{results['cols_count']} x {results['rows_count']}")

        st.markdown("### Planta Baixa Digital e Disposição de Carteiras")
        
        # POLÍTICA DE SEGURO CONTRA ERRO DE MÓDULO (FALLBACK DINÂMICO)
        if HAS_MATPLOTLIB:
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.set_xlim(-0.5, room_w + 0.5)
                ax.set_ylim(-0.5, room_d + 0.5)
                ax.add_patch(patches.Rectangle((0, 0), room_w, room_d, linewidth=2, edgecolor='black', facecolor='#f8f9fa'))
                ax.add_patch(patches.Rectangle((0, 0), room_w, corr_front, linewidth=1, edgecolor='red', facecolor='red', alpha=0.08, linestyle='--'))
                
                for obs in st.session_state.obstacles:
                    ax.add_patch(patches.Rectangle((obs.x, obs.y), obs.w, obs.d, linewidth=1, edgecolor='darkred', facecolor='darkred', alpha=0.6))
                
                for d in results["desks_coords"]:
                    ax.add_patch(patches.Rectangle((d["x1"], d["y1"]), desk_w, desk_d, linewidth=1, edgecolor='#1C83E1', facecolor='#1C83E1', alpha=0.4))
                
                ax.set_aspect('equal')
                st.pyplot(fig)
                plt.close(fig)
            except Exception:
                st.info("ℹ️ Gráfico vetorial indisponível temporariamente no servidor. Exibindo matriz de mapeamento discreto abaixo:")
                st.dataframe(pd.DataFrame(results["desks_coords"]), use_container_width=True)
        else:
            st.info("ℹ️ Modo de segurança ativo. Coordenadas exatas das carteiras calculadas para auditoria:")
            st.dataframe(pd.DataFrame(results["desks_coords"]), use_container_width=True)

        st.markdown("### Balanço de Utilização de Superfície")
        df_chart = pd.DataFrame({
            "Área Ocupada (m²)": [results["occupied_area"]],
            "Área Livre/Circulação (m²)": [results["free_area"]]
        })
        st.bar_chart(df_chart.T)

    with tab_simulation:
        st.header("Análise Comparativa de Cenários de Alocação")
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
        st.table(pd.DataFrame(sim_data))

if __name__ == "__main__":
    main()
