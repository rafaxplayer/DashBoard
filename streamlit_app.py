import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import json
import shutil
from pathlib import Path
from html import escape
from urllib.parse import urlparse

DATA_FILE = Path('investments_streamlit.json')
BACKUP_FILE = DATA_FILE.with_suffix(DATA_FILE.suffix + '.bak')
INVESTMENT_CATEGORIES = (
    'Otros',
    'Acciones',
    'ETF',
    'Fondos idx',
    'CrowdLending',
    'C. Remunerada',
    'Depositos',
)

st.set_page_config(page_title='Mis inversiones', layout='wide')

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

    [data-testid="stForm"] {
        margin-top: 1rem;
    }

    .add-form-gap {
        height: 1.5rem;
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

    [data-testid="stButton"] button[aria-label="Editar inversión"] {
        min-width: 42px;
        padding: 0.5rem;
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
        font-size: 14px;
    }

    .benefits-table-scroll {
        max-width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }

    .benefits-table th {
        background: var(--purple);
        color: white;
        font-size: 13px;
        font-weight: 700;
        padding: 0.65rem 0.5rem;
        text-align: left;
    }

    div[data-testid="stDataFrame"] {
        font-size: 1rem !important;
    }

    div[data-testid="stDataFrame"] thead th {
        background: #1f5ca8 !important;
        color: white !important;
        font-size: 1.02rem !important;
        font-weight: 700 !important;
    }

    div[data-testid="stDataFrame"] tbody td {
        font-size: 1rem !important;
    }

    .benefits-table td {
        border-bottom: 1px solid #454b61;
        padding: 0.65rem 0.5rem;
        white-space: nowrap;
    }

    .benefits-table tr:hover td {
        background: #3b4156;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 1rem 1.5rem !important;
        }

        .st-key-benefits_allocation_layout .stHorizontalBlock {
            flex-direction: column;
        }

        .st-key-benefits_allocation_layout .stColumn {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .benefits-table {
            min-width: 500px;
            font-size: 12px;
        }

        .benefits-table th {
            font-size: 11px;
            padding: 0.55rem 0.4rem;
        }

        .benefits-table td {
            padding: 0.55rem 0.4rem;
        }
    }

    .portfolio-header {
        display: grid;
        grid-template-columns: 1.7fr 1.3fr 1fr 1fr 0.8fr;
        gap: 0.8rem;
        background: var(--purple);
        color: white;
        font-size: 16px;
        font-weight: 700;
        padding: 0.75rem 0.65rem;
        margin-bottom: 1rem;
    }

    .portfolio-name {
        color: var(--text);
        font-weight: 600;
        line-height: 1.25;
    }

    .portfolio-category {
        display: inline-block;
        margin-top: 0.35rem;
        padding: 0.18rem 0.5rem;
        background: rgba(94, 73, 245, 0.22);
        border: 1px solid rgba(164, 150, 255, 0.7);
        border-radius: 999px;
        color: #dfe6ff;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-transform: none;
    }

    .transfer-info {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 1.05rem;
        height: 1.05rem;
        margin-left: 0.35rem;
        color: #b8b0ff;
        font-size: 0.85rem;
        cursor: help;
        vertical-align: text-top;
    }

    .transfer-info-tooltip {
        position: absolute;
        z-index: 10;
        left: 1.25rem;
        top: -0.35rem;
        display: none;
        width: 260px;
        padding: 0.75rem 0.85rem;
        background: #171a25;
        border: 1px solid #5b6380;
        border-radius: 3px;
        color: var(--text);
        font-size: 0.85rem;
        font-weight: 400;
        line-height: 1.45;
        white-space: pre-line;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35);
    }

    .transfer-info:hover .transfer-info-tooltip {
        display: block;
    }

    .portfolio-note {
        color: var(--muted);
        font-size: 0.9rem;
        font-weight: 400;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
        overflow: hidden;
        margin-top: 0.25rem;
    }
</style>
''', unsafe_allow_html=True)

def load_data():
    transfer_fields = ('beneficiary', 'bank_name', 'account_number', 'bic_swift', 'payment_reference')
    if DATA_FILE.exists():
        with DATA_FILE.open('r', encoding='utf-8') as data_file:
            stored_data = json.load(data_file)
        investments = stored_data.get('investments', []) if isinstance(stored_data, dict) else stored_data
        df = pd.DataFrame(investments)
        if 'category' not in df.columns:
            df['category'] = 'Otros'
        if 'link' not in df.columns:
            df['link'] = ''
        if 'note' not in df.columns:
            df['note'] = ''
        df['category'] = df['category'].fillna('Otros').astype(str)
        df['note'] = df['note'].fillna('').astype(str)
        for field in transfer_fields:
            if field not in df.columns:
                df[field] = ''
            df[field] = df[field].fillna('').astype(str)
        return df[['name', 'category', 'link', 'amount', 'roi', 'note', *transfer_fields]]
    else:
        df = pd.DataFrame([
            {'name':'BTC','category':'Acciones','link':'https://bitcoin.org/','amount':12000.0,'roi':18.5,'note':'', **dict.fromkeys(transfer_fields, '')},
            {'name':'ETF Global','category':'ETF','link':'','amount':8000.0,'roi':6.2,'note':'', **dict.fromkeys(transfer_fields, '')},
            {'name':'Ahorros','category':'Depositos','link':'','amount':2000.0,'roi':1.1,'note':'', **dict.fromkeys(transfer_fields, '')}
        ])
        save_data(df)
        return df

def load_reserved_investments():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open('r', encoding='utf-8') as data_file:
        stored_data = json.load(data_file)
    reserved = stored_data.get('reserved_investments', []) if isinstance(stored_data, dict) else []
    fields = ('name', 'category', 'link', 'amount', 'roi', 'note', 'beneficiary', 'bank_name',
              'account_number', 'bic_swift', 'payment_reference')
    normalized = []
    for investment in reserved:
        item = {field: investment.get(field, '') for field in fields}
        item['name'] = str(item['name']) or 'Sin nombre'
        item['category'] = str(item.get('category') or 'Otros')
        item['link'] = str(item['link'])
        amount = pd.to_numeric(item['amount'], errors='coerce')
        roi = pd.to_numeric(item['roi'], errors='coerce')
        item['amount'] = float(0.0 if pd.isna(amount) else amount)
        item['roi'] = float(0.0 if pd.isna(roi) else roi)
        for field in fields[5:]:
            item[field] = str(item[field] or '')
        normalized.append(item)
    return normalized

def save_data(df):
    save_all_data(df, load_banks())

def save_all_data(df, banks, reserved=None):
    if reserved is None:
        reserved = load_reserved_investments()
    write_data_file(
        {
            'investments': df.to_dict(orient='records'),
            'banks': banks.to_dict(orient='records'),
            'reserved_investments': reserved,
        }
    )

def write_data_file(data):
    if DATA_FILE.exists():
        shutil.copy2(DATA_FILE, BACKUP_FILE)
    temporary_file = DATA_FILE.with_suffix(DATA_FILE.suffix + '.tmp')
    with temporary_file.open('w', encoding='utf-8') as data_file:
        json.dump(
            data,
            data_file,
            ensure_ascii=False,
            indent=2,
        )
    temporary_file.replace(DATA_FILE)

def validate_import_data(data):
    if isinstance(data, list):
        data = {'investments': data}
    if not isinstance(data, dict):
        raise ValueError('El JSON debe contener un objeto de datos.')

    investments = data.get('investments')
    banks = data.get('banks', [])
    reserved = data.get('reserved_investments', [])
    if not isinstance(investments, list) or not investments:
        raise ValueError('El archivo debe incluir al menos una inversión.')
    if not all(isinstance(item, dict) for item in investments):
        raise ValueError('La lista de inversiones no tiene un formato válido.')
    if not all(field in item for item in investments for field in ('name', 'amount', 'roi')):
        raise ValueError('Cada inversión debe incluir nombre, importe y rentabilidad.')
    if not isinstance(banks, list) or not all(isinstance(item, dict) for item in banks):
        raise ValueError('La lista de bancos no tiene un formato válido.')
    if not isinstance(reserved, list) or not all(isinstance(item, dict) for item in reserved):
        raise ValueError('La lista de inversiones reservadas no tiene un formato válido.')
    return {
        'investments': investments,
        'banks': banks,
        'reserved_investments': reserved,
    }

def load_banks():
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=['name', 'iban', 'bic_swift', 'holder'])
    with DATA_FILE.open('r', encoding='utf-8') as data_file:
        stored_data = json.load(data_file)
    banks = stored_data.get('banks', []) if isinstance(stored_data, dict) else []
    df = pd.DataFrame(banks)
    for field in ('name', 'iban', 'bic_swift', 'holder'):
        if field not in df.columns:
            df[field] = ''
        df[field] = df[field].fillna('').astype(str)
    return df[['name', 'iban', 'bic_swift', 'holder']]

def bank_widget_id(bank):
    values = tuple(str(bank.get(field, '')) for field in ('name', 'iban', 'bic_swift', 'holder'))
    return hashlib.sha1(repr(values).encode('utf-8')).hexdigest()[:12]

def request_bank_delete(row_index, bank):
    st.session_state.pending_bank_delete = {
        'row_index': int(row_index),
        'bank': bank,
    }

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

def transfer_info_html(investment):
    fields = (
        ('Beneficiario', 'beneficiary'),
        ('Nombre de banco', 'bank_name'),
        ('Número de cuenta', 'account_number'),
        ('BIC/SWIFT', 'bic_swift'),
        ('Referencia de pago', 'payment_reference'),
    )
    values = [(label, str(investment.get(key, '')).strip()) for label, key in fields]
    if not any(value for _, value in values):
        return ''
    tooltip = '<br>'.join(
        f'<strong>{escape(label)}:</strong> {escape(value) if value else "-"}'
        for label, value in values
    )
    return (
        '<span class="transfer-info" aria-label="Datos de transferencia">ⓘ'
        f'<span class="transfer-info-tooltip">{tooltip}</span></span>'
    )

def request_delete(row_index, investment):
    st.session_state.pending_delete = {
        'row_index': int(row_index),
        'investment': investment,
    }

def request_reserved_dialog():
    st.session_state.show_reserved_dialog = True

def investment_name_key(value):
    return ' '.join(str(value).strip().casefold().split())

@st.dialog('Inversiones en reserva')
def reserved_investments_dialog():
    reserved = st.session_state.reserved_investments
    if not reserved:
        st.info('No hay inversiones guardadas en reserva.')
        return
    st.write('Selecciona una inversión para cargar sus datos en el formulario de alta.')
    for reserve_index, investment in enumerate(reserved):
        item_col, action_col = st.columns([4, 1])
        with item_col:
            st.write(investment['name'])
            st.caption(f'{format_euros(investment["amount"])} · {investment["roi"]:.2f}%')
        with action_col:
            if st.button(
                '',
                icon=':material/add_circle:',
                help=f'Usar {investment["name"]}',
                key=f'use_reserved_{reserve_index}',
                use_container_width=True,
            ):
                st.session_state.selected_reserved_index = reserve_index
                st.session_state.load_reserved_form = True
                st.session_state.show_reserved_dialog = False
                st.rerun()

def add_investment_from_form():
    name = st.session_state.get('new_name', '').strip() or 'Sin nombre'
    name_key = investment_name_key(name)
    existing_names = {
        investment_name_key(value)
        for value in st.session_state.df['name']
    }
    selected = st.session_state.get('selected_reserved_index')
    reserved_names = {
        investment_name_key(investment['name'])
        for reserve_index, investment in enumerate(st.session_state.reserved_investments)
        if reserve_index != selected
    }
    if name_key in existing_names or name_key in reserved_names:
        st.session_state.investment_form_error = (
            f'Ya existe una inversión con el nombre «{name}» en el portfolio o en reserva.'
        )
        return

    new = pd.DataFrame([{
        'name': name,
        'category': st.session_state.get('new_category', 'Otros').strip() or 'Otros',
        'link': st.session_state.get('new_link', '').strip(),
        'amount': float(st.session_state.get('new_amount', 0.0)),
        'roi': float(st.session_state.get('new_roi', 0.0)),
        'note': st.session_state.get('new_note', '').strip(),
        'beneficiary': st.session_state.get('new_beneficiary', '').strip(),
        'bank_name': st.session_state.get('new_bank_name', '').strip(),
        'account_number': st.session_state.get('new_account_number', '').strip(),
        'bic_swift': st.session_state.get('new_bic_swift', '').strip(),
        'payment_reference': st.session_state.get('new_payment_reference', '').strip(),
    }])
    st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
    if selected is not None and selected < len(st.session_state.reserved_investments):
        st.session_state.reserved_investments.pop(selected)
    st.session_state.selected_reserved_index = None
    st.session_state.load_reserved_form = False
    for field in (
        'new_name', 'new_category', 'new_link', 'new_note', 'new_beneficiary', 'new_bank_name',
        'new_account_number', 'new_bic_swift', 'new_payment_reference',
    ):
        st.session_state[field] = ''
    st.session_state.new_amount = 0.0
    st.session_state.new_roi = 0.0
    save_all_data(
        st.session_state.df,
        st.session_state.banks,
        st.session_state.reserved_investments,
    )
    st.session_state.notification = {
        'message': 'Inversión añadida correctamente',
        'icon': '✅',
    }

def request_edit(row_index):
    st.session_state.pending_edit = int(row_index)

@st.dialog('Editar inversión')
def edit_investment_dialog(row_index):
    investment = st.session_state.df.loc[row_index]
    with st.form(f'edit_form_{row_index}'):
        name = st.text_input('Nombre / Inversión', value=str(investment['name']))
        category = st.selectbox(
            'Categoría',
            options=INVESTMENT_CATEGORIES,
            index=INVESTMENT_CATEGORIES.index(str(investment.get('category', 'Otros')))
            if str(investment.get('category', 'Otros')) in INVESTMENT_CATEGORIES else 0,
        )
        link = st.text_input('Enlace', value=str(investment.get('link', '')), placeholder='https://...')
        amount = st.number_input('Cantidad invertida (€)', min_value=0.0, value=float(investment['amount']), step=0.01)
        roi = st.number_input('Rentabilidad (%)', value=float(investment['roi']), step=0.01)
        note = st.text_area('Nota', value=str(investment.get('note', '')), placeholder='Añade una nota sobre esta inversión...')
        with st.expander('Datos de transferencia', expanded=False):
            beneficiary = st.text_input('Beneficiario', value=str(investment.get('beneficiary', '')))
            bank_name = st.text_input('Nombre de banco', value=str(investment.get('bank_name', '')))
            account_number = st.text_input('Número de cuenta', value=str(investment.get('account_number', '')))
            bic_swift = st.text_input('BIC/SWIFT', value=str(investment.get('bic_swift', '')))
            payment_reference = st.text_input('Referencia de pago', value=str(investment.get('payment_reference', '')))
        save_col, cancel_col = st.columns(2)
        with save_col:
            save = st.form_submit_button('Guardar', type='primary', use_container_width=True)
        with cancel_col:
            cancel = st.form_submit_button('Cancelar', use_container_width=True)

    if cancel:
        st.session_state.pending_edit = None
        st.rerun()
    if save:
        st.session_state.df.loc[row_index, [
            'name', 'category', 'link', 'amount', 'roi', 'note', 'beneficiary', 'bank_name',
            'account_number', 'bic_swift', 'payment_reference',
        ]] = [
            name or 'Sin nombre', category, link.strip(), float(amount), float(roi), note.strip(),
            beneficiary.strip(), bank_name.strip(), account_number.strip(),
            bic_swift.strip(), payment_reference.strip(),
        ]
        save_data(st.session_state.df)
        st.session_state.pending_edit = None
        st.session_state.notification = {'message': 'Inversión actualizada correctamente', 'icon': '✅'}
        st.rerun()

def investment_widget_id(investment):
    values = tuple(str(investment.get(field, '')) for field in ('name', 'link', 'amount', 'roi'))
    return hashlib.sha1(repr(values).encode('utf-8')).hexdigest()[:12]

@st.cache_data
def generate_colors(n):
    pool = ['#7c5cff','#00d4ff','#ff6b6b','#ffd166','#4ade80','#60a5fa','#d946ef','#ff8c42']
    return [pool[i % len(pool)] for i in range(n)]

@st.dialog('Backups')
def backups_dialog():
    st.write('Exporta todos tus datos o importa un archivo JSON para restaurarlos.')
    st.caption(f'La copia automática anterior se guarda en `{BACKUP_FILE.name}`.')

    st.download_button(
        'Exportar datos JSON',
        DATA_FILE.read_text(encoding='utf-8'),
        file_name='investments_streamlit.json',
        mime='application/json',
        icon=':material/download:',
        width='stretch',
    )

    uploaded_data = st.file_uploader(
        'Archivo JSON o respaldo .bak',
        type=['json', 'bak'],
        key='data_import_file',
    )
    if st.button('Importar datos', icon=':material/upload:', disabled=uploaded_data is None):
        try:
            imported_data = validate_import_data(
                json.loads(uploaded_data.getvalue().decode('utf-8'))
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
            st.error(f'No se pudieron importar los datos: {error}')
        else:
            write_data_file(imported_data)
            for state_key in (
                'df', 'banks', 'reserved_investments', 'pending_edit',
                'pending_delete', 'pending_bank_delete', 'show_reserved_dialog',
            ):
                st.session_state.pop(state_key, None)
            st.session_state.notification = {
                'message': 'Datos importados correctamente. Se creó una copia de seguridad.',
                'icon': '✅',
            }
            st.rerun()

def main():
    st.title('Mis inversiones')

    notification = st.session_state.pop('notification', None)
    if notification:
        st.toast(notification['message'], icon=notification['icon'])
    form_error = st.session_state.pop('investment_form_error', None)
    if form_error:
        st.error(form_error)

    # Load or initialize
    if 'df' not in st.session_state:
        st.session_state.df = load_data()
    elif 'link' not in st.session_state.df.columns:
        st.session_state.df['link'] = ''
    if 'category' not in st.session_state.df.columns:
        st.session_state.df['category'] = 'Otros'
    if 'note' not in st.session_state.df.columns:
        st.session_state.df['note'] = ''
    st.session_state.df['category'] = st.session_state.df['category'].fillna('Otros').astype(str)
    st.session_state.df['note'] = st.session_state.df['note'].fillna('').astype(str)
    transfer_fields = ('beneficiary', 'bank_name', 'account_number', 'bic_swift', 'payment_reference')
    for field in transfer_fields:
        if field not in st.session_state.df.columns:
            st.session_state.df[field] = ''
        st.session_state.df[field] = st.session_state.df[field].fillna('').astype(str)
    st.session_state.df = st.session_state.df[['name', 'category', 'link', 'amount', 'roi', 'note', *transfer_fields]]
    if 'banks' not in st.session_state:
        st.session_state.banks = load_banks()
    st.session_state.banks = st.session_state.banks[['name', 'iban', 'bic_swift', 'holder']]
    if 'reserved_investments' not in st.session_state:
        st.session_state.reserved_investments = load_reserved_investments()

    pending_edit = st.session_state.get('pending_edit')
    if pending_edit is not None and pending_edit in st.session_state.df.index:
        edit_investment_dialog(pending_edit)
    if st.session_state.get('show_reserved_dialog'):
        st.session_state.show_reserved_dialog = False
        reserved_investments_dialog()

    with st.container(horizontal=True, horizontal_alignment='right'):
        csv = st.session_state.df.to_csv(index=False)
        st.download_button(
            'Exportar CSV',
            csv,
            file_name='investments.csv',
            icon=':material/download:',
        )
        if st.button('Backups', icon=':material/backup:'):
            backups_dialog()

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
        save_for_later = st.checkbox(
            'Guardar datos para futuras inversiones',
            key=f'save_deleted_{pending_index}',
        )
        confirm_col, cancel_col, _ = st.columns([1, 1, 3])
        with confirm_col:
            if st.button('Confirmar eliminación', type='primary', key='confirm_delete'):
                if save_for_later:
                    st.session_state.reserved_investments.append(
                        st.session_state.df.loc[pending_index].to_dict()
                    )
                st.session_state.df = st.session_state.df.drop(index=pending_index).reset_index(drop=True)
                save_all_data(
                    st.session_state.df,
                    st.session_state.banks,
                    st.session_state.reserved_investments,
                )
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
            title_col, reserve_col = st.columns([5, 1])
            with title_col:
                st.header('Añadir inversión')
            if st.session_state.reserved_investments:
                with reserve_col:
                    st.button(
                        '',
                        icon=':material/inventory_2:',
                        help='Abrir inversiones en reserva',
                        type='secondary',
                        key='open_reserved_investments',
                        on_click=request_reserved_dialog,
                        use_container_width=True,
                    )
            st.markdown('<div class="add-form-gap"></div>', unsafe_allow_html=True)
            with st.form('add_form'):
                selected = st.session_state.get('selected_reserved_index')
                selected_investment = (
                    st.session_state.reserved_investments[selected]
                    if selected is not None and selected < len(st.session_state.reserved_investments)
                    else {}
                )
                new_values = {
                    'new_name': selected_investment.get('name', ''),
                    'new_category': selected_investment.get('category', 'Acciones'),
                    'new_link': selected_investment.get('link', ''),
                    'new_amount': float(selected_investment.get('amount', 0.0)),
                    'new_roi': float(selected_investment.get('roi', 0.0)),
                    'new_note': selected_investment.get('note', ''),
                    'new_beneficiary': selected_investment.get('beneficiary', ''),
                    'new_bank_name': selected_investment.get('bank_name', ''),
                    'new_account_number': selected_investment.get('account_number', ''),
                    'new_bic_swift': selected_investment.get('bic_swift', ''),
                    'new_payment_reference': selected_investment.get('payment_reference', ''),
                }
                if st.session_state.pop('load_reserved_form', False):
                    for field, value in new_values.items():
                        st.session_state[field] = value
                for field, value in new_values.items():
                    st.session_state.setdefault(field, value)
                name = st.text_input('Nombre / Inversión', key='new_name')
                category = st.selectbox(
                    'Categoría',
                    options=INVESTMENT_CATEGORIES,
                    index=0,
                    key='new_category',
                )
                link = st.text_input('Enlace', placeholder='https://...', key='new_link')
                amount = st.number_input('Cantidad invertida (€)', min_value=0.0, step=0.01, key='new_amount')
                roi = st.number_input('Rentabilidad (%)', step=0.01, key='new_roi')
                note = st.text_area('Nota', placeholder='Añade una nota sobre esta inversión...', key='new_note')
                with st.expander('Datos de transferencia', expanded=False):
                    beneficiary = st.text_input('Beneficiario', key='new_beneficiary')
                    bank_name = st.text_input('Nombre de banco', key='new_bank_name')
                    account_number = st.text_input('Número de cuenta', key='new_account_number')
                    bic_swift = st.text_input('BIC/SWIFT', key='new_bic_swift')
                    payment_reference = st.text_input('Referencia de pago', key='new_payment_reference')
                st.form_submit_button(
                    'Añadir inversión',
                    on_click=add_investment_from_form,
                )

        with row1_col2:
            st.header('Portfolio')
            sort_options = {
                'Nombre': 'name',
                'Categoría': 'category',
                'Invertido (€)': 'amount',
                'Rentabilidad (%)': 'roi',
            }
            portfolio_sort = st.selectbox(
                'Ordenar portfolio por',
                options=list(sort_options.keys()),
                index=1,
                help='Ordena el portfolio de mayor a menor según la columna seleccionada.',
            )
            if 'pending_edit' in st.session_state and st.session_state.pending_edit is not None:
                st.session_state.pending_edit = None
            if 'pending_delete' in st.session_state and st.session_state.pending_delete is not None:
                st.session_state.pending_delete = None
            portfolio_df = st.session_state.df.sort_values(
                sort_options[portfolio_sort],
                ascending=False,
                kind='stable',
            )
            st.markdown(
                '<div class="portfolio-header"><span>Nombre / Plataforma</span>'
                '<span>Enlace</span><span>Invertido (€)</span><span>Rentabilidad (%)</span>'
                '<span></span></div>',
                unsafe_allow_html=True,
            )
            portfolio_rows = []
            for row_index, investment in portfolio_df.iterrows():
                widget_id = investment_widget_id(investment)
                name_col, link_col, amount_col, roi_col, actions_col = st.columns(
                    [1.7, 1.3, 1, 1, 0.8],
                    vertical_alignment='center',
                )
                with name_col:
                    note = escape(str(investment.get('note', '')).strip())
                    category = escape(str(investment.get('category', 'Otros')).strip() or 'Otros')
                    note_html = f'<div class="portfolio-note">{note}</div>' if note else ''
                    st.markdown(
                        f'<div class="portfolio-name">{escape(str(investment["name"]))}'
                        f'{transfer_info_html(investment)}'
                        f'<div class="portfolio-category">{category}</div>'
                        f'{note_html}</div>',
                        unsafe_allow_html=True,
                    )
                with link_col:
                    link = safe_link(investment.get('link', ''))
                    st.markdown(f'[Abrir enlace]({link})' if link else 'Sin enlace')
                with amount_col:
                    st.write(format_euros(float(investment['amount'])))
                with roi_col:
                    st.write(f'{float(investment["roi"]):.2f}%')
                with actions_col:
                    edit_col, delete_col = st.columns(2, vertical_alignment='center')
                    with edit_col:
                        st.button(
                            '',
                            icon=':material/edit:',
                            help='Editar inversión',
                            type='secondary',
                            key=f'portfolio_edit_{widget_id}',
                            on_click=request_edit,
                            args=(row_index,),
                            use_container_width=True,
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
                            use_container_width=True,
                        )

            df = compute_derived(st.session_state.df)
            st.metric('Total invertido', format_euros(df['amount'].sum()))

    st.divider()
    with st.container(border=True, key='benefits_allocation_layout'):
        row2_col1, row2_col2 = st.columns([1, 1])

        with row2_col1:
            chart_mode = st.radio(
                'Vista de distribución',
                options=['Por inversión', 'Por categoría'],
                horizontal=True,
                index=0,
            )
            st.subheader(
                'Distribución por porcentaje por categoría' if chart_mode == 'Por categoría'
                else 'Distribución por porcentaje'
            )
            total_invested = df['amount'].sum()
            if chart_mode == 'Por categoría':
                category_df = df.groupby('category', dropna=False).agg(amount=('amount', 'sum')).reset_index()
                category_df['category'] = category_df['category'].fillna('Otros').astype(str)
                category_df['percent'] = (category_df['amount'] / category_df['amount'].sum() * 100.0).fillna(0.0)
                chart_df = category_df.sort_values('amount', ascending=False, kind='stable')
                names_col = 'category'
                values_col = 'amount'
                hover_template = '<b>%{label}</b><br>%{percent}<br>%{value:,.2f} €<extra></extra>'
            else:
                chart_df = df.sort_values('allocation_pct', ascending=False, kind='stable')
                names_col = 'name'
                values_col = 'amount'
                hover_template = '<b>%{label}</b><br>%{percent}<br>%{value:,.2f} €<extra></extra>'
            fig = px.pie(
                chart_df,
                names=names_col,
                values=values_col,
                hole=0.58,
                color_discrete_sequence=generate_colors(len(chart_df)),
            )
            fig.update_traces(
                sort=False,
                direction='clockwise',
                rotation=0,
                textinfo='label+percent',
                textposition='outside',
                automargin=True,
                textfont_size=12,
                hovertemplate=hover_template,
            )
            fig.update_layout(
                template='plotly_dark',
                height=600,
                margin=dict(t=30, b=30, l=50, r=50),
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
            sort_options = {
                'Invertido': 'amount',
                'Rentabilidad (%)': 'roi',
                'Beneficio': 'profit',
                '% Asignación': 'allocation_pct',
            }
            sort_column = st.selectbox(
                'Ordenar por',
                options=list(sort_options.keys()),
                index=2,
                help='Ordena la tabla por la columna seleccionada de mayor a menor.',
            )
            display_df = df.sort_values(sort_options[sort_column], ascending=False, kind='stable')
            display_df = display_df[['name','amount','roi','profit','allocation_pct']].rename(columns={
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
                '<div class="benefits-table-scroll">'
                f'{display_df.to_html(index=False, classes="benefits-table", escape=False)}'
                '</div>',
                unsafe_allow_html=True,
            )

    st.divider()
    with st.container(border=True):
        st.header('Bancos')
        form_col, table_col = st.columns([1, 2])

        with form_col:
            st.subheader('Añadir banco')
            with st.form('bank_add_form'):
                bank_name = st.text_input('Nombre del Banco')
                iban = st.text_input('IBAN')
                bic_swift = st.text_input('BIC/SWIFT')
                holder = st.text_input('Titular')
                add_bank = st.form_submit_button('Añadir banco')
                if add_bank:
                    new_bank = pd.DataFrame([{
                        'name': bank_name.strip() or 'Sin nombre',
                        'iban': iban.strip(),
                        'bic_swift': bic_swift.strip(),
                        'holder': holder.strip(),
                    }])
                    st.session_state.banks = pd.concat(
                        [st.session_state.banks, new_bank], ignore_index=True
                    )
                    save_all_data(st.session_state.df, st.session_state.banks)
                    st.session_state.notification = {
                        'message': 'Banco añadido correctamente',
                        'icon': '✅',
                    }
                    st.rerun()

        with table_col:
            pending_bank_delete = st.session_state.get('pending_bank_delete')
            pending_bank_index = None
            pending_bank_name = None
            if isinstance(pending_bank_delete, dict):
                pending_bank = pending_bank_delete['bank']
                candidate_indices = st.session_state.banks.index
                for field, value in pending_bank.items():
                    candidate_indices = candidate_indices[
                        st.session_state.banks.loc[candidate_indices, field].eq(value)
                    ]
                if len(candidate_indices):
                    original_index = pending_bank_delete['row_index']
                    pending_bank_index = (
                        original_index
                        if original_index in candidate_indices
                        else candidate_indices[0]
                    )
                    pending_bank_name = st.session_state.banks.loc[pending_bank_index, 'name']

            if pending_bank_index is not None:
                st.warning(f'¿Seguro que quieres eliminar el banco «{pending_bank_name}»?')
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button('Confirmar eliminación', type='primary', key='confirm_bank_delete'):
                        st.session_state.banks = st.session_state.banks.drop(
                            index=pending_bank_index
                        ).reset_index(drop=True)
                        save_all_data(st.session_state.df, st.session_state.banks)
                        st.session_state.pending_bank_delete = None
                        st.session_state.notification = {
                            'message': f'Banco «{pending_bank_name}» eliminado',
                            'icon': '🗑️',
                        }
                        st.rerun()
                with cancel_col:
                    if st.button('Cancelar', key='cancel_bank_delete'):
                        st.session_state.pending_bank_delete = None
                        st.rerun()

            st.markdown(
                '<div class="portfolio-header"><span>Nombre del Banco</span>'
                '<span>IBAN</span><span>BIC/SWIFT</span><span>Titular</span>'
                '<span></span></div>',
                unsafe_allow_html=True,
            )
            for row_index, bank in st.session_state.banks.iterrows():
                widget_id = bank_widget_id(bank)
                name_col, iban_col, bic_col, holder_col, actions_col = st.columns(
                    [1.2, 1.7, 1.1, 1.2, 0.45]
                )
                with name_col:
                    st.markdown(
                        f'<strong style="color: white">{escape(str(bank["name"]))}</strong>',
                        unsafe_allow_html=True,
                    )
                with iban_col:
                    st.write(bank['iban'] or 'Sin IBAN')
                with bic_col:
                    st.write(bank['bic_swift'] or 'Sin BIC/SWIFT')
                with holder_col:
                    st.write(bank['holder'] or 'Sin titular')
                with actions_col:
                    st.button(
                        '',
                        icon=':material/delete:',
                        help='Eliminar banco',
                        type='secondary',
                        key=f'bank_delete_{widget_id}',
                        on_click=request_bank_delete,
                        args=(row_index, bank.to_dict()),
                        use_container_width=True,
                    )

    st.caption('Los datos se guardan localmente en `investments_streamlit.json`')

if __name__ == '__main__':
    main()
