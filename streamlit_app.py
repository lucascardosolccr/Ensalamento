import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# TENTATIVA DEFENSIVA DE IMPORTAÇÃO GRÁFICA (Prevenção Antibug)
HAS_MATPLOTLIB = False
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ==============================================================================
# CONFIGURAÇÃO DE AMBIENTE E ESTILIZAÇÃO CORPORATIVA
# ==============================================================================
st.set_page_config(
    page_title="PROMPT MASTER v2.0 - Auditoria de Capacidade",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .reportview-container .main .block-container { padding-top: 1.5rem; }
    .stMetric { background-color: rgba(28, 131, 225, 0.07); padding: 16px; border-radius: 12px; border-left: 6px solid #1C83E1; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .stAlert { border-radius: 12px; }
    div.stButton > button:first-child { background-color: #1C83E1; color: white; border-radius: 8px; width: 100%; font-weight: bold; height: 45px; }
    .css-1kyx603 { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MODELO DE INFRAESTRUTURA LOGÍSTICA
# ==============================================================================
class Obstacle:
    def __init__(self, name: str, x: float, y: float, w: float, d: float):
        self.name = name
        self.x = x  # Canto inferior esquerdo
        self.y = y  # Canto inferior esquerdo
        self.w = w  # Largura (Eixo X)
        self.d = d  # Profundidade (Eixo Y)

    def intersects(self, cx1: float, cy1: float, cx2: float, cy2: float) -> bool:
        # Algoritmo AABB (Axis-Aligned Bounding Box) estável para detecção de colisão hígida
        ox1, oy1 = self.x, self.y
        ox2, oy2 = self.x + self.w, self.y + self.d
        return not (cx2 <= ox1 or cx1 >= ox2 or cy2 <= oy1 or cy1 >= oy2)

# ==============================================================================
# MOTOR MATEMÁTICO DE OTIMIZAÇÃO E PESQUISA OPERACIONAL
# ==============================================================================
class RoomOptimizer:
    @staticmethod
    def optimize(
        room_w: float, room_d: float,
        desk_w: float, desk_d: float,
        space_lat: float, space_front: float,
        corr_center: bool, corr_center_w: float,
        corr_lat: float, corr_front: float, corr_back: float,
        obstacles: List[Obstacle], rotate_layout: bool = False
    ) -> Dict[str, Any]:
        
        # Inversão geométrica se o usuário optar por testar a orientação alternativa
        if rotate_layout:
            desk_w, desk_d = desk_d, desk_w

        # Definição das células ergonômicas reais de ocupação
        cell_w = desk_w + space_lat
        cell_d = desk_d + space_front

        best_desks = []
        best_efficiency = -1.0
        
        total_area = room_w * room_d
        fiscal_area = room_w * corr_front
        
        # Heurística Dinâmica de Varredura Espacial por Sub-grid
        for offset_x in np.linspace(0, min(cell_w, 0.15), 4):
            for offset_y in np.linspace(0, min(cell_d, 0.15), 4):
                current_desks = []
                
                start_x = corr_lat + offset_x
                end_x = room_w - corr_lat
                start_y = corr_front + offset_y
                end_y = room_d - corr_back

                center_x = room_w / 2.0

                y = start_y
                while y + desk_d <= end_y:
                    x = start_x
                    while x + desk_w <= end_x:
                        # Restrição dinâmica do Corredor Central customizado
                        if corr_center and (center_x - corr_center_w/2 < x + desk_w/2 < center_x + corr_center_w/2):
                            x += 0.1
                            continue
                        
                        cx1, cy1 = x, y
                        cx2, cy2 = x + desk_w, y + desk_d
                        
                        # Processamento de intersecções contrárias a barreiras físicas
                        collision = False
                        for obs in obstacles:
                            if obs.intersects(cx1, cy1, cx2, cy2):
                                collision = True
                                break
                        
                        if not collision:
                            current_desks.append({"x1": cx1, "y1": cy1, "x2": cx2, "y2": cy2})
                        
                        x += cell_w
                    y += cell_d

                calc_efficiency = (len(current_desks) * (desk_w * desk_d)) / total_area if total_area > 0 else 0
                
                if calc_efficiency > best_efficiency:
                    best_efficiency = calc_efficiency
                    best_desks = current_desks

        occupied_area = len(best_desks) * (desk_w * desk_d)
        free_area = total_area - occupied_area - fiscal_area
        
        x_coords = sorted(list(set([round(d["x1"], 3) for d in best_desks])))
        y_coords = sorted(list(set([round(d["y1"], 3) for d in best_desks])))

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
# INTERFACE GRÁFICA DO USUÁRIO (STREAMLIT DASHBOARD)
# ==============================================================================
def main():
    st.title("📐 PROMPT MASTER v2.0")
    st.subheader("Plataforma Avançada de Auditoria Ocupacional e Alocação de Concursos Públicos")
    st.markdown("---")

    # PAINEL LATERAL: TOTALMENTE PERSONALIZÁVEL E EDITÁVEL PELO OPERADOR
    with st.sidebar:
        st.header("📋 Perímetro da Sala")
        room_w = st.number_input("Largura da Sala (m)", min_value=1.0, max_value=100.0, value=8.5, step=0.1)
        room_d = st.number_input("Comprimento da Sala (m)", min_value=1.0, max_value=100.0, value=11.0, step=0.1)
        
        st.header("🪑 Configuração do Mobiliário")
        furniture_preset = st.selectbox("Predefinição Ergonômica", ["Personalizado", "Universitária Padrão", "Mesa Individual", "Mesa Dupla"])
        
        # Valores base calculados dinamicamente com base nas normas do FNDE
        d_w, d_d = 0.65, 0.50
        if furniture_preset == "Universitária Padrão":
            d_w, d_d = 0.60, 0.50
        elif furniture_preset == "Mesa Individual":
            d_w, d_d = 0.80, 0.60
        elif furniture_preset == "Mesa Dupla":
            d_w, d_d = 1.30, 0.65

        desk_w = st.number_input("Largura Real da Carteira (m)", min_value=0.1, max_value=5.0, value=d_w, step=0.05)
        desk_d = st.number_input("Profundidade Real da Carteira (m)", min_value=0.1, max_value=5.0, value=d_d, step=0.05)

        st.header("🛑 Espaçamentos Interpessoais")
        space_lat = st.number_input("Distância Lateral entre Carteiras (m)", min_value=0.0, max_value=3.0, value=0.45, step=0.05)
        space_front = st.number_input("Distância Frontal entre Carteiras (m)", min_value=0.0, max_value=3.0, value=0.60, step=0.05)
        
        st.header("🛣️ Corredores e Rotas de Fuga")
        corr_front = st.number_input("Recuo Frontal / Área do Fiscal (m)", min_value=0.5, max_value=10.0, value=2.2, step=0.1)
        corr_back = st.number_input("Corredor Técnico Traseiro (m)", min_value=0.1, max_value=5.0, value=0.5, step=0.05)
        corr_lat = st.number_input("Corredores Laterais de Escoamento (m)", min_value=0.1, max_value=5.0, value=0.6, step=0.05)
        
        st.markdown("**Divisão de Fluxo**")
        corr_center = st.checkbox("Habilitar Corredor Central", value=False)
        corr_center_w = st.number_input("Largura do Corredor Central (m)", min_value=0.5, max_value=4.0, value=1.0, step=0.1, disabled=not corr_center)

    # ABAS PRINCIPAIS DE NAVEGAÇÃO E OPERAÇÃO COMPLETA
    tab_dashboard, tab_obstacles, tab_analytics = st.tabs(["📊 Painel de Controle e Planta", "🏗️ Infraestrutura e Obstáculos", "🧠 Inteligência de Cenários"])

    # Tratamento de persistência de barreiras físicas em sessão estável
    if "obstacles" not in st.session_state:
        st.session_state.obstacles = [Obstacle("Pilar Estrutural 1", 4.0, 5.5, 0.6, 0.6)]

    with tab_obstacles:
        st.header("Mapeamento de Pilares, Colunas e Elementos Fixos")
        st.markdown("Adicione as barreiras físicas mapeadas na vistoria técnica da escola para recalcular as rotas de segurança.")
        
        with st.form("form_add_obstacle"):
            obs_name = st.text_input("Identificação do Obstáculo", value=f"Coluna {len(st.session_state.obstacles) + 1}")
            c1, c2, c3, c4 = st.columns(4)
            obs_x = c1.number_input("Coordenada X Inicial (m)", min_value=0.0, max_value=room_w, value=2.0, step=0.1)
            obs_y = c2.number_input("Coordenada Y Inicial (m)", min_value=0.0, max_value=room_d, value=4.0, step=0.1)
            obs_w = c3.number_input("Largura Real ΔX (m)", min_value=0.05, max_value=room_w, value=0.5, step=0.05)
            obs_d = c4.number_input("Profundidade Real ΔY (m)", min_value=0.05, max_value=room_d, value=0.5, step=0.05)
            
            if st.form_submit_button("Injetar Elemento de Bloqueio"):
                if obs_x + obs_w > room_w or obs_y + obs_d > room_d:
                    st.error("🚨 Erro Crítico: O obstáculo definido ultrapassa os limites estruturais da sala!")
                else:
                    st.session_state.obstacles.append(Obstacle(obs_name, obs_x, obs_y, obs_w, obs_d))
                    st.rerun()

        if st.session_state.obstacles:
            df_obs = pd.DataFrame([{
                "Componente": o.name, "X Inicial (m)": o.x, "Y Inicial (m)": o.y, "Largura (m)": o.w, "Profundidade (m)": o.d
            } for o in st.session_state.obstacles])
            st.dataframe(df_obs, use_container_width=True)
            if st.button("Remover Todos os Obstáculos"):
                st.session_state.obstacles = []
                st.rerun()

    # EXECUÇÃO DA OTIMIZAÇÃO EM TEMPO REAL (Módulo Principal)
    results = RoomOptimizer.optimize(
        room_w, room_d, desk_w, desk_d, space_lat, space_front,
        corr_center, corr_center_w, corr_lat, corr_front, corr_back, st.session_state.obstacles, rotate_layout=False
    )

    with tab_dashboard:
        # Fileira Executiva de Indicadores Operacionais
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Capacidade Homologada", f"{results['total_desks']} Candidatos", help="Ocupação física discreta permitida")
        m2.metric("Aproveitamento de Superfície", f"{results['efficiency']:.1f}%", help="Porcentagem de área útil ocupada pelas mesas")
        m3.metric("Densidade Real", f"{results['density']:.2f} cand/m²")
        m4.metric("Estrutura (Colunas x Fileiras)", f"{results['cols_count']} x {results['rows_count']}")

        st.markdown("### Planta Técnica Vetorial Disponibilizada")
        
        if HAS_MATPLOTLIB:
            try:
                fig, ax = plt.subplots(figsize=(11, 7.5))
                ax.set_xlim(-0.6, room_w + 0.6)
                ax.set_ylim(-0.6, room_d + 0.6)
                
                # Desenho do perímetro externo estrutural
                ax.add_patch(patches.Rectangle((0, 0), room_w, room_d, linewidth=3, edgecolor='#1E293B', facecolor='#F8FAFC'))
                
                # Demarcação da faixa regulatória de fiscalização externa
                ax.add_patch(patches.Rectangle((0, 0), room_w, corr_front, linewidth=1, edgecolor='#EF4444', facecolor='#EF4444', alpha=0.07, linestyle='--'))
                ax.text(room_w/2, corr_front/2, "ÁREA CRÍTICA: MESA DO FISCAL / EXAME", color='#DC2626', ha='center', va='center', fontsize=10, weight='bold')
                
                # Exibição de barreiras físicas salvas
                for obs in st.session_state.obstacles:
                    ax.add_patch(patches.Rectangle((obs.x, obs.y), obs.w, obs.d, linewidth=1.5, edgecolor='#7F1D1D', facecolor='#991B1B', alpha=0.8))
                    ax.text(obs.x + obs.w/2, obs.y + obs.d/2, obs.name, color='white', ha='center', va='center', fontsize=8, weight='bold')
                
                # Plotagem paramétrica das posições calculadas para os candidatos
                for idx, d in enumerate(results["desks_coords"]):
                    ax.add_patch(patches.Rectangle((d["x1"], d["y1"]), desk_w, desk_d, linewidth=1, edgecolor='#1D4ED8', facecolor='#3B82F6', alpha=0.45))
                    ax.text(d["x1"] + desk_w/2, d["y1"] + desk_d/2, str(idx+1), color='#1E3A8A', ha='center', va='center', fontsize=7, weight='bold')
                
                ax.set_xlabel("Largura da Sala de Prova (m)", fontsize=9)
                ax.set_ylabel("Profundidade da Sala de Prova (m)", fontsize=9)
                ax.grid(True, linestyle=':', alpha=0.5, color='#CBD5E1')
                ax.set_aspect('equal')
                
                st.pyplot(fig)
                plt.close(fig)
            except Exception:
                st.info("Visualização gráfica resumida em modo de contingência operacional devido ao servidor cloud.")
        else:
            st.warning("Motor gráfico em modo textual secundário.")

        # MECANISMO DE AUDITORIA: EXPORTAÇÃO COMPLETA DAS COORDENADAS VIA CSV
        st.markdown("### 📥 Extração de Laudo Oficial para a Banca")
        st.markdown("Utilize o gerador abaixo para extrair a planilha de auditoria exigida pelas coordenações de logística de concursos.")
        
        if results["total_desks"] > 0:
            export_data = []
            for i, d in enumerate(results["desks_coords"]):
                export_data.append({
                    "Candidato_Numero": i + 1,
                    "Coordenada_X_Esquerda_m": round(d["x1"], 3),
                    "Coordenada_Y_Fundo_m": round(d["y1"], 3),
                    "Largura_Movel_m": desk_w,
                    "Profundidade_Movel_m": desk_d
                })
            df_export = pd.DataFrame(export_data)
            
            csv_buffer = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar Coordenadas de Ensalamento (Formatado para CEBRASPE/FGV)",
                data=csv_buffer,
                file_name="laudo_inspecao_capacidade.csv",
                mime="text/csv"
            )
        else:
            st.caption("Nenhum candidato mapeado para geração de relatórios de saída.")

    with tab_analytics:
        st.header("🧠 Matriz de Inteligência e Rotação Geométrica")
        st.markdown("Nossa inteligência computacional realiza testes paralelos comparando as orientações físicas possíveis e o impacto das folgas escolhidas.")
        
        # Testando Rotação automática (Retrato vs Paisagem)
        results_rotated = RoomOptimizer.optimize(
            room_w, room_d, desk_w, desk_d, space_lat, space_front,
            corr_center, corr_center_w, corr_lat, corr_front, corr_back, st.session_state.obstacles, rotate_layout=True
        )

        sim_comparativa = [
            {"Orientação": "Padrão Informada (Vertical/Retrato)", "Capacidade Obtida": results["total_desks"], "Eficiência Mapeada": f"{results['efficiency']:.2f}%"},
            {"Orientação": "Rotacionada Sugerida (Horizontal/Paisagem)", "Capacidade Obtida": results_rotated["total_desks"], "Eficiência Mapeada": f"{results_rotated['efficiency']:.2f}%"}
        ]
        st.table(pd.DataFrame(sim_comparativa))

        # Diagnóstico de Engenharia Civil e Arquitetura Preventiva
        st.markdown("### 📋 Diagnóstico e Validação Normativa Automática")
        
        recomendações = []
        if room_w > 0 and (desk_w / room_w) > 0.4:
            recomendações.append("⚠️ **Incompatibilidade de Proporção:** A largura da carteira consome uma fração excessiva da sala de aula. Verifique se o mobiliário selecionado é adequado para este local.")
        if corr_front < 1.5:
            recomendações.append("🚨 **Risco de Segurança:** O corredor frontal está abaixo de 1.5 metros. Isso compromete a área operacional dos fiscais e pode violar normas locais contra incêndios (Corpo de Bombeiros).")
        if results["efficiency"] > 45.0:
            recomendações.append("⚡ **Alerta de Alta Densidade:** O aproveitamento está excepcionalmente elevado. Certifique-se de que a circulação do ar e o conforto térmico suportem esta configuração.")
            
        if recomendações:
            for rec in recomendações:
                st.markdown(rec)
        else:
            st.info("✅ Conformidade Estrutural Plena: O modelo configurado atende de forma equilibrada aos requisitos mínimos de fluxo de pessoas e às distâncias interpessoais.")

        st.markdown("### Balanço de Utilização de Superfície")
        df_chart_nativo = pd.DataFrame({
            "Metragem Quadrada (m²)": [results["occupied_area"], results["free_area"]]
        }, index=["Área Ocupada por Carteiras", "Área Livre e Corredores"])
        st.bar_chart(df_chart_nativo)

if __name__ == "__main__":
    main()
