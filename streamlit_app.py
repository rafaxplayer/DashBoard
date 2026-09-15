import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
from pathlib import Path
from html import escape
from urllib.parse import urlparse

DATA_FILE = Path('investments_streamlit.json')

st.set_page_config(page_title='Dashboard de Inversiones', layout='wide')

st.markdown('''
<style>
    :root {
        --dashboard-bg: #292d3d;
        --panel-bg: #33384b;
        --panel-deep: #252938;
        --line: #1d2230;
        --text: #f1f3f8;
        --muted: #9299ad;
        --purple: #5e49f5;
        --green: #3bc99e;
        --yellow: #f5c400;
        --orange: #ff4b0b;
    }

    .stApp {
        background: var(--dashboard-bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1440px;
        padding: 2.5rem 3rem 2rem;
        font-size: 1.08rem;
    }

    h1, h2, h3 {
        color: var(--text) !important;
        letter-spacing: 0.02em;
    }

    h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.2rem !important;
    }

    h2, h3 {
        font-weight: 600 !important;
    }

    h2 {
        font-size: 1.45rem !important;
    }

    h3 {
        font-size: 1.25rem !important;
    }

    [data-testid="stCaptionContainer"], .stMarkdown p {
        color: var(--muted);
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--panel-bg);
        border: 2px solid var(--line);
        border-radius: 2px;
        padding: 1rem 1.2rem;
    }

    label, [data-testid="stWidgetLabel"] p {
        font-size: 1.05rem !important;
    }

    input, textarea, [data-baseweb="select"] > div {
        font-size: 1.05rem !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        font-size: 18px !important;
        min-height: 46px;
    }

    [data-testid="stMetric"] {
        background: var(--panel-deep);
        border-left: 4px solid var(--purple);
        padding: 0.8rem 1rem;
        border-radius: 2px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 1.55rem !important;
    }

    [data-testid="stButton"] button,
    [data-testid="stDownloadButton"] button,
    [data-testid="stFormSubmitButton"] button {
        background: var(--purple);
        color: white;
        border: 1px solid #796aff;
        border-radius: 2px;
        font-weight: 600;
    }

    [data-testid="stButton"] button:hover,
    [data-testid="stDownloadButton"] button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        background: #735fff;
        border-color: #a198ff;
        color: white;
    }

    [data-testid="stFormSubmitButton"] button[aria-label="Eliminar"] {
        background: #ff5a36;
        border-color: #ff9a82;
        min-width: 42px;
        padding: 0.5rem;
    }

    [data-testid="stFormSubmitButton"] button[aria-label="Eliminar"]:hover {
        background: #ff7658;
        border-color: #ffc0b2;
    }

    [data-testid="stFormSubmitButton"] button[aria-label="Eliminar"] p {
        display: none;
    }

    [data-testid="stFormSubmitButton"] button[aria-label="Eliminar"] span {
        font-size: 1.25rem !important;
    }

    input, textarea, [data-baseweb="select"] > div {
        background: var(--panel-deep) !important;
        color: var(--text) !important;
        border-color: #454b61 !important;
        border-radius: 2px !important;
    }

    hr {
        border-color: var(--line) !important;
        margin: 1.4rem 0 !important;
    }

    [data-testid="stAlert"] {
        border-radius: 2px;
        background: #244b47;
        border: 1px solid var(--green);
    }

    .benefits-table {
        width: 100%;
        border-collapse: collapse;
        background: var(--panel-deep);
        color: var(--text);
        font-size: 18px;
    }

    .benefits-table th {
        background: var(--purple);
        color: white;
        font-size: 16px;
        font-weight: 700;
        padding: 0.8rem 0.65rem;
        text-align: left;
    }

    .benefits-table td {
        border-bottom: 1px solid #454b61;
        padding: 0.85rem 0.65rem;
        white-space: nowrap;
    }

    .benefits-table tr:hover td {
        background: #3b4156;
    }

    .portfolio-header {
        display: grid;
        grid-template-columns: 1.7fr 1.3fr 1fr 1fr 0.5fr;
        gap: 0.8rem;
        background: var(--purple);
        color: white;
        font-size: 16px;
        font-weight: 700;
        padding: 0.75rem 0.65rem;
    }
</style>
''', unsafe_allow_html=True)

def load_data():
    if DATA_FILE.exists():
        df = pd.read_json(DATA_FILE)
        if 'link' not in df.columns:
            df['link'] = ''
        return df[['name', 'link', 'amount', 'roi']]
    else:
        df = pd.DataFrame([
            {'name':'BTC','link':'https://bitcoin.org/','amount':12000.0,'roi':18.5},
            {'name':'ETF Global','link':'','amount':8000.0,'roi':6.2},
            {'name':'Ahorros','link':'','amount':2000.0,'roi':1.1}
        ])
        save_data(df)
        return df

def save_data(df):
    df.to_json(DATA_FILE, orient='records', indent=2)

def compute_derived(df):
    df = df.copy()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    df['roi'] = pd.to_numeric(df['roi'], errors='coerce').fillna(0.0)
    df['profit'] = df['amount'] * df['roi'] / 100.0
    total = df['amount'].sum()
    df['allocation_pct'] = (df['amount'] / total * 100.0).fillna(0.0)
    return df

def format_euros(value):
    return f'{value:,.2f} €'.replace(',', 'X').replace('.', ',').replace('X', '.')

def safe_link(value):
    link = str(value).strip()
    parsed = urlparse(link)
    if parsed.scheme in ('http', 'https') and parsed.netloc:
        return link
    return ''

def request_delete(row_index, investment):
    st.session_state.pending_delete = {
        'row_index': int(row_index),
        'investment': investment,
    }

def investment_widget_id(investment):
    values = tuple(str(investment.get(field, '')) for field in ('name', 'link', 'amount', 'roi'))
    return hashlib.sha1(repr(values).encode('utf-8')).hexdigest()[:12]

@st.cache_data
def generate_colors(n):
    pool = ['#7c5cff','#00d4ff','#ff6b6b','#ffd166','#4ade80','#60a5fa','#d946ef','#ff8c42']
    return [pool[i % len(pool)] for i in range(n)]

def main():
    st.title('Dashboard de Inversiones')

    notification = st.session_state.pop('notification', None)
    if notification:
        st.toast(notification['message'], icon=notification['icon'])

    # Load or initialize
    if 'df' not in st.session_state:
        st.session_state.df = load_data()
    elif 'link' not in st.session_state.df.columns:
        st.session_state.df['link'] = ''
    st.session_state.df = st.session_state.df[['name', 'link', 'amount', 'roi']]

    with st.container():
        csv = st.session_state.df.to_csv(index=False)
        st.download_button('Exportar CSV', csv, file_name='investments.csv', use_container_width=True)

    st.divider()

    pending_delete = st.session_state.get('pending_delete')
    pending_index = None
    pending_name = None
    if isinstance(pending_delete, dict):
        pending_investment = pending_delete['investment']
        candidate_indices = st.session_state.df.index
        for field, value in pending_investment.items():
            candidate_indices = candidate_indices[
                st.session_state.df.loc[candidate_indices, field].eq(value)
            ]
        if len(candidate_indices):
            original_index = pending_delete['row_index']
            pending_index = (
                original_index
                if original_index in candidate_indices
                else candidate_indices[0]
            )
            pending_name = st.session_state.df.loc[pending_index, 'name']

    if pending_index is not None:
        st.warning(f'¿Seguro que quieres eliminar la inversión «{pending_name}»?')
        confirm_col, cancel_col, _ = st.columns([1, 1, 3])
        with confirm_col:
            if st.button('Confirmar eliminación', type='primary', key='confirm_delete'):
                st.session_state.df = st.session_state.df.drop(index=pending_index).reset_index(drop=True)
                save_data(st.session_state.df)
                st.session_state.pending_delete = None
                st.session_state.notification = {
                    'message': f'Inversión «{pending_name}» eliminada',
                    'icon': '🗑️',
                }
                st.rerun()
        with cancel_col:
            if st.button('Cancelar', key='cancel_delete'):
                st.session_state.pending_delete = None
                st.rerun()

    with st.container(border=True):
        row1_col1, row1_col2 = st.columns([1, 2])

        with row1_col1:
            st.header('Añadir inversión')
            with st.form('add_form'):
                name = st.text_input('Nombre / Inversión', value='')
                link = st.text_input('Enlace', value='', placeholder='https://...')
                amount = st.number_input('Cantidad invertida (€)', min_value=0.0, value=0.0, step=0.01)
                roi = st.number_input('Rentabilidad (%)', value=0.0, step=0.01)
                add = st.form_submit_button('Añadir inversión')
                if add:
                    new = pd.DataFrame([{
                        'name': name or 'Sin nombre',
                        'link': link.strip(),
                        'amount': float(amount),
                        'roi': float(roi),
                    }])
                    st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
                    save_data(st.session_state.df)
                    st.session_state.notification = {
                        'message': 'Inversión añadida correctamente',
                        'icon': '✅',
                    }
                    st.rerun()

        with row1_col2:
            st.header('Portfolio')
            st.markdown(
                '<div class="portfolio-header"><span>Nombre / Plataforma</span>'
                '<span>Enlace</span><span>Invertido (€)</span><span>Rentabilidad (%)</span>'
                '<span></span></div>',
                unsafe_allow_html=True,
            )
            portfolio_rows = []
            for row_index, investment in st.session_state.df.iterrows():
                widget_id = investment_widget_id(investment)
                name_col, link_col, amount_col, roi_col, delete_col = st.columns([1.7, 1.3, 1, 1, 0.5])
                with name_col:
                    edited_name = st.text_input(
                        'Nombre',
                        value=str(investment['name']),
                        key=f'portfolio_name_{widget_id}',
                        label_visibility='collapsed',
                    )
                with link_col:
                    edited_link = st.text_input(
                        'Enlace',
                        value=str(investment.get('link', '')),
                        key=f'portfolio_link_{widget_id}',
                        placeholder='https://...',
                        label_visibility='collapsed',
                    )
                with amount_col:
                    edited_amount = st.number_input(
                        'Invertido',
                        min_value=0.0,
                        value=float(investment['amount']),
                        step=0.01,
                        key=f'portfolio_amount_{widget_id}',
                        label_visibility='collapsed',
                    )
                with roi_col:
                    edited_roi = st.number_input(
                        'Rentabilidad',
                        value=float(investment['roi']),
                        step=0.01,
                        key=f'portfolio_roi_{widget_id}',
                        label_visibility='collapsed',
                    )
                with delete_col:
                    st.button(
                        '',
                        icon=':material/delete:',
                        help='Eliminar inversión',
                        type='secondary',
                        key=f'portfolio_delete_{widget_id}',
                        on_click=request_delete,
                        args=(row_index, investment.to_dict()),
                    )
                portfolio_rows.append({
                    'name': edited_name,
                    'link': edited_link,
                    'amount': edited_amount,
                    'roi': edited_roi,
                })

            if st.button('Guardar edición del portfolio', use_container_width=True):
                st.session_state.df = pd.DataFrame(portfolio_rows, columns=['name', 'link', 'amount', 'roi'])
                save_data(st.session_state.df)
                st.session_state.notification = {
                    'message': 'Cambios del portfolio guardados',
                    'icon': '✅',
                }
                st.rerun()

            df = compute_derived(st.session_state.df)
            st.metric('Total invertido', format_euros(df['amount'].sum()))

    st.divider()
    with st.container(border=True):
        row2_col1, row2_col2 = st.columns([1, 1])

        with row2_col1:
            st.subheader('Distribución por porcentaje')
            total_invested = df['amount'].sum()
            fig = px.pie(
                df,
                names='name',
                values='amount',
                hole=0.58,
                color_discrete_sequence=generate_colors(len(df)),
            )
            fig.update_traces(
                textinfo='percent',
                textposition='inside',
                hovertemplate='<b>%{label}</b><br>%{percent}<br>%{value:,.2f} €<extra></extra>',
            )
            fig.update_layout(
                template='plotly_dark',
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='#33384b',
                plot_bgcolor='#33384b',
                legend=dict(font=dict(color='#f1f3f8')),
                annotations=[{
                    'text': f'<b>{format_euros(total_invested)}</b><br><span style="font-size:11px">TOTAL</span>',
                    'showarrow': False,
                    'font': {'color': '#f1f3f8', 'size': 15},
                }],
            )
            st.plotly_chart(fig, use_container_width=True)

        with row2_col2:
            st.subheader('Tabla con beneficios y asignación')
            display_df = df[['name','amount','roi','profit','allocation_pct']].rename(columns={
                'name':'Nombre','amount':'Invertido','roi':'Rentabilidad (%)','profit':'Beneficio','allocation_pct':'% Asignación'
            })
            display_df['Nombre'] = display_df.apply(
                lambda row: (
                    f'<a href="{escape(safe_link(df.loc[row.name, "link"]), quote=True)}" '
                    'target="_blank" rel="noopener noreferrer">'
                    f'{escape(str(row["Nombre"]))}</a>'
                    if safe_link(df.loc[row.name, 'link'])
                    else escape(str(row['Nombre']))
                ),
                axis=1,
            )
            display_df['Invertido'] = display_df['Invertido'].map(format_euros)
            display_df['Beneficio'] = display_df['Beneficio'].map(format_euros)
            display_df['% Asignación'] = display_df['% Asignación'].map(lambda value: f'{value:.1f}%')
            st.markdown(
                display_df.to_html(index=False, classes='benefits-table', escape=False),
                unsafe_allow_html=True,
            )

    st.caption('Los datos se guardan localmente en `investments_streamlit.json`')

if __name__ == '__main__':
    main()
