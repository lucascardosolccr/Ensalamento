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
    page_title="PROMPT MASTER v3.0 - Processamento em Lote",
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
        self.x = x
        self.y = y
        self.w = w
        self.d = d

    def intersects(self, cx1: float, cy1: float, cx2: float, cy2: float) -> bool:
        ox1, oy1 = self.x, self.y
        ox2, oy2 = self.x + self.w, self.y + self.d
        return not (cx2 <= ox1 or cx1 >= ox2 or cy2 <= oy1 or cy1 >= oy2)

# ==============================================================================
# MOTOR MATEMÁTICO DE OTIMIZAÇÃO (CÁLCULO INDEPENDENTE POR LINHA)
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
        
        if rotate_layout:
            desk_w, desk_d = desk_d, desk_w

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
                        if corr_center and (center_x - corr_center_w/2 < x + desk_w/2 < center_x + corr_center_w/2):
                            x += 0.1
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
# INTERFACE GRÁFICA DO USUÁRIO
# ==============================================================================
def main():
    st.title("📐 PROMPT MASTER v3.0")
    st.subheader("Auditoria em Lote e Alocação Ocupacional Computadorizada")
    st.markdown("---")

    # ABAS DO SISTEMA (Preservando Simulação de Sala Única + Injetando Modo Planilha)
    tab_bulk, tab_single, tab_obstacles = st.tabs([
        "📥 Processamento em Lote (Planilha)", 
        "📊 Modo Sala Individual (Painel Interativo)", 
        "🏗️ Infraestrutura e Obstáculos"
    ])

    # Inicialização estável das variáveis de sessão para barreiras fixas
    if "obstacles" not in st.session_state:
        st.session_state.obstacles = [Obstacle("Pilar Estrutural 1", 4.0, 5.5, 0.6, 0.6)]

    # ==============================================================================
    # ABA 1: PROCESSAMENTO EM LOTE (NOVA FUNCIONALIDADE SOLICITADA)
    # ==============================================================================
    with tab_bulk:
        st.header("Processamento Automatizado de Multi-Salas")
        st.markdown("Carregue seu arquivo contendo as medições de múltiplos espaços e mapeie os parâmetros logo abaixo.")

        uploaded_file = st.file_uploader("Selecione sua Planilha (Formatos aceitos: .csv, .xlsx)", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            # Leitura dinâmica baseada na extensão
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_input = pd.read_csv(uploaded_file)
                else:
                    df_input = pd.read_excel(uploaded_file)
                
                st.success(f"Planilha carregada com sucesso! Identificamos {len(df_input)} linhas/salas catalogadas.")
                
                # Interface inteligente de de-para/mapeamento de colunas obrigatórias
                st.markdown("### 🔍 Mapeamento Técnico de Dimensões")
                st.info("Informe ao motor de cálculo em quais colunas da sua planilha original estão guardadas cada uma das dimensões:")
                
                all_cols = df_input.columns.tolist()
                
                col_a, col_b = st.columns(2)
                c_id = col_a.selectbox("Nome da Sala / Identificador", all_cols, index=0)
                c_rw = col_a.selectbox("Largura da Sala (m)", all_cols, index=min(1, len(all_cols)-1))
                c_rd = col_a.selectbox("Comprimento da Sala (m)", all_cols, index=min(2, len(all_cols)-1))
                c_dw = col_a.selectbox("Largura da Carteira/Mesa (m)", all_cols, index=min(3, len(all_cols)-1))
                c_dd = col_b.selectbox("Profundidade da Carteira/Mesa (m)", all_cols, index=min(4, len(all_cols)-1))
                c_sl = col_b.selectbox("Espaçamento Lateral Mínimo (m)", all_cols, index=min(5, len(all_cols)-1))
                c_sf = col_b.selectbox("Espaçamento Frontal Mínimo (m)", all_cols, index=min(6, len(all_cols)-1))
                
                with st.expander("🛠️ Parametrizar Colunas de Corredores (Opcional - Padrão Fixo se não houver coluna)"):
                    has_corr_cols = st.checkbox("Minha planilha possui colunas específicas para corredores", value=False)
                    if has_corr_cols:
                        c_cf = st.selectbox("Corredor Frontal / Fiscal (m)", all_cols)
                        c_cb = st.selectbox("Corredor Traseiro (m)", all_cols)
                        c_cl = st.selectbox("Corredores Laterais (m)", all_cols)
                    else:
                        st.caption("Usando os valores padrão padrão de mercado: Fiscal: 2.2m, Traseiro: 0.5m, Laterais: 0.6m.")
                        f_cf, f_cb, f_cl = 2.2, 0.5, 0.6

                # Botão de Execução Massiva
                if st.button("🚀 Processar e Auditar Planilha Completa"):
                    results_bulk = []
                    
                    for index, row in df_input.iterrows():
                        # Extração segura e conversão numérica por segurança
                        try:
                            sala_name = str(row[c_id])
                            r_w = float(row[c_rw])
                            r_d = float(row[c_rd])
                            d_w = float(row[c_dw])
                            d_d = float(row[c_dd])
                            s_l = float(row[c_sl])
                            s_f = float(row[c_sf])
                            
                            cf = float(row[c_cf]) if has_corr_cols else f_cf
                            cb = float(row[c_cb]) if has_corr_cols else f_cb
                            cl = float(row[c_cl]) if has_corr_cols else f_cl
                            
                            # Cálculo individual da linha
                            res = RoomOptimizer.optimize(
                                room_w=r_w, room_d=r_d, desk_w=d_w, desk_d=d_d,
                                space_lat=s_l, space_front=s_f, corr_center=False, corr_center_w=1.0,
                                corr_lat=cl, corr_front=cf, corr_back=cb, obstacles=[]
                            )
                            
                            results_bulk.append({
                                "Capacidade_Vagas": res["total_desks"],
                                "Eficiencia_Espacial_%": round(res["efficiency"], 2),
                                "Densidade_Cand_m2": round(res["density"], 2),
                                "Colunas_Calculadas": res["cols_count"],
                                "Fileiras_Calculadas": res["rows_count"]
                            })
                        except Exception as row_err:
                            # Prevenção de quebra do lote se houver linha em branco ou erro de digitação
                            results_bulk.append({
                                "Capacidade_Vagas": 0, "Eficiencia_Espacial_%": 0.0, "Densidade_Cand_m2": 0.0,
                                "Colunas_Calculadas": 0, "Fileiras_Calculadas": 0
                            })

                    # Fusão dos dados processados com as colunas originais do usuário (Sem perdas)
                    df_output = df_input.copy()
                    df_res_cols = pd.DataFrame(results_bulk)
                    for col in df_res_cols.columns:
                        df_output[col] = df_res_cols[col]

                    # Métricas globais consolidadas
                    st.markdown("### 🏆 Resultado Consolidado da Auditoria")
                    v1, v2, v3 = st.columns(3)
                    v1.metric("Total Geral de Vagas Mapeadas", f"{int(df_output['Capacidade_Vagas'].sum())} Alunos")
                    v2.metric("Média de Eficiência das Salas", f"{df_output['Eficiencia_Espacial_%'].mean():.1f}%")
                    v3.metric("Maior Capacidade Unidade Única", f"{int(df_output['Capacidade_Vagas'].max())} Alunos")

                    st.dataframe(df_output, use_container_width=True)

                    # Exportação imediata
                    csv_bulk_buffer = df_output.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Baixar Planilha de Resultados Processados (.CSV)",
                        data=csv_bulk_buffer,
                        file_name="relatorio_lote_ensalamento.csv",
                        mime="text/csv"
                    )

            except Exception as file_err:
                st.error(f"Erro na leitura do arquivo. Certifique-se de que ele não está corrompido ou protegido por senha. Detalhes: {file_err}")
        else:
            st.info("Aguardando upload de planilha para ativar o motor de cálculo em lote.")

    # ==============================================================================
    # ABA 2: MODO SALA INDIVIDUAL (PRESERVAÇÃO INTEGRAL SEM REGRESSÃO)
    # ==============================================================================
    with tab_single:
        with st.sidebar:
            st.markdown("---")
            st.header("⚙️ Variáveis de Ajuste Fino (Sala Única)")
            room_w = st.number_input("Largura da Sala (m)", min_value=1.0, max_value=100.0, value=8.5, key="single_rw")
            room_d = st.number_input("Comprimento da Sala (m)", min_value=1.0, max_value=100.0, value=11.0, key="single_rd")
            
            furniture_preset = st.selectbox("Predefinição Ergonômica", ["Personalizado", "Universitária Padrão", "Mesa Individual"], key="single_fp")
            d_w, d_d = 0.65, 0.50
            if furniture_preset == "Universitária Padrão": d_w, d_d = 0.60, 0.50
            elif furniture_preset == "Mesa Individual": d_w, d_d = 0.80, 0.60
            
            desk_w = st.number_input("Largura Real da Carteira (m)", min_value=0.1, max_value=5.0, value=d_w, key="single_dw")
            desk_d = st.number_input("Profundidade Real da Carteira (m)", min_value=0.1, max_value=5.0, value=d_d, key="single_dd")
            space_lat = st.number_input("Distância Lateral entre Carteiras (m)", min_value=0.0, max_value=3.0, value=0.45, key="single_sl")
            space_front = st.number_input("Distância Frontal entre Carteiras (m)", min_value=0.0, max_value=3.0, value=0.60, key="single_sf")
            corr_front = st.number_input("Recuo Frontal / Área do Fiscal (m)", min_value=0.5, max_value=10.0, value=2.2, key="single_cf")
            corr_back = st.number_input("Corredor Técnico Traseiro (m)", min_value=0.1, max_value=5.0, value=0.5, key="single_cb")
            corr_lat = st.number_input("Corredores Laterais (m)", min_value=0.1, max_value=5.0, value=0.6, key="single_cl")
            corr_center = st.checkbox("Habilitar Corredor Central", value=False, key="single_cc")
            corr_center_w = st.number_input("Largura do Corredor Central (m)", min_value=0.5, max_value=4.0, value=1.0, key="single_ccw", disabled=not corr_center)

        # Execução Sala Única
        results = RoomOptimizer.optimize(
            room_w, room_d, desk_w, desk_d, space_lat, space_front,
            corr_center, corr_center_w, corr_lat, corr_front, corr_back, st.session_state.obstacles, rotate_layout=False
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Capacidade Homologada", f"{results['total_desks']} Candidatos")
        m2.metric("Aproveitamento de Superfície", f"{results['efficiency']:.1f}%")
        m3.metric("Densidade Real", f"{results['density']:.2f} cand/m²")
        m4.metric("Estrutura", f"{results['cols_count']} x {results['rows_count']}")

        # Renderização gráfica segura
        if HAS_MATPLOTLIB:
            try:
                fig, ax = plt.subplots(figsize=(11, 6.5))
                ax.set_xlim(-0.6, room_w + 0.6)
                ax.set_ylim(-0.6, room_d + 0.6)
                ax.add_patch(patches.Rectangle((0, 0), room_w, room_d, linewidth=3, edgecolor='#1E293B', facecolor='#F8FAFC'))
                ax.add_patch(patches.Rectangle((0, 0), room_w, corr_front, linewidth=1, edgecolor='#EF4444', facecolor='#EF4444', alpha=0.07, linestyle='--'))
                
                for obs in st.session_state.obstacles:
                    ax.add_patch(patches.Rectangle((obs.x, obs.y), obs.w, obs.d, linewidth=1.5, edgecolor='#7F1D1D', facecolor='#991B1B', alpha=0.8))
                for idx, d in enumerate(results["desks_coords"]):
                    ax.add_patch(patches.Rectangle((d["x1"], d["y1"]), desk_w, desk_d, linewidth=1, edgecolor='#1D4ED8', facecolor='#3B82F6', alpha=0.45))
                    ax.text(d["x1"] + desk_w/2, d["y1"] + desk_d/2, str(idx+1), color='#1E3A8A', ha='center', va='center', fontsize=7, weight='bold')
                
                ax.set_aspect('equal')
                st.pyplot(fig)
                plt.close(fig)
            except Exception:
                st.info("Exibindo matriz de mapeamento em modo texto.")

    # ==============================================================================
    # ABA 3: GESTÃO DE OBSTÁCULOS
    # ==============================================================================
    with tab_obstacles:
        st.header("Mapeamento de Barreiras Físicas (Pilares e Colunas Fixas)")
        with st.form("form_add_obstacle_v3"):
            obs_name = st.text_input("Identificação do Obstáculo", value=f"Coluna {len(st.session_state.obstacles) + 1}")
            c1, c2, c3, c4 = st.columns(4)
            obs_x = c1.number_input("Coordenada X Inicial (m)", min_value=0.0, max_value=10.0, value=2.0)
            obs_y = c2.number_input("Coordenada Y Inicial (m)", min_value=0.0, max_value=10.0, value=4.0)
            obs_w = c3.number_input("Largura Real ΔX (m)", min_value=0.05, max_value=5.0, value=0.5)
            obs_d = c4.number_input("Profundidade Real ΔY (m)", min_value=0.05, max_value=5.0, value=0.5)
            
            if st.form_submit_button("Injetar Elemento de Bloqueio"):
                st.session_state.obstacles.append(Obstacle(obs_name, obs_x, obs_y, obs_w, obs_d))
                st.rerun()

        if st.session_state.obstacles:
            df_obs = pd.DataFrame([{
                "Componente": o.name, "X Inicial (m)": o.x, "Y Inicial (m)": o.y, "Largura (m)": o.w, "Profundidade (m)": o.d
            } for o in st.session_state.obstacles])
            st.dataframe(df_obs, use_container_width=True)
            if st.button("Remover Todos os Obstáculos", key="clear_obs_bulk"):
                st.session_state.obstacles = []
                st.rerun()

if __name__ == "__main__":
    main()
