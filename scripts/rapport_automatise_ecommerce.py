# -*- coding: utf-8 -*-
"""Rapport_automatise_ecommerce.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GUZYsHfMff64ukQx_QETAP_-eL62rMfv
"""

import pandas as pd
import plotly.express as px
import base64
import pdfkit
from jinja2 import Environment, FileSystemLoader, Template
import argparse

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input','-i',   default='Amazon Sale Report.csv', help="Chemin du CSV")
    p.add_argument('--width',  type=int, default=1600,             help="Largeur des images")
    p.add_argument('--height', type=int, default=800,              help="Hauteur des images")
    p.add_argument('--scale',  type=int, default=2,                help="Échelle des images")
    args, _ = p.parse_known_args()
    return args

def load_data(path_csv):
    df = pd.read_csv(path_csv, low_memory=False)
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%m-%d-%y', errors='coerce')
    return df

# Récupèration des périodes mensuelles
def get_periods(df):
    return (
        df['Date']
          .dt.to_period('M')
          .dropna()
          .drop_duplicates()
          .sort_values()
    )

# Calcul KPIs pour un sous-DataFrame d’un mois
def compute_kpis(df_mois):
    ca     = df_mois['Amount'].sum()
    orders = df_mois['Order ID'].nunique()
    qty    = df_mois['Qty'].sum()
    profit = df_mois['Profit'].sum() if 'Profit' in df_mois else None
    return ca, orders, qty, profit

# Génération et export des figures
def make_plots(df_mois, year, month, month_name, width, height, scale):
    def encode_png(path):
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()

    daily = (
      df_mois.groupby(df_mois['Date'].dt.date)['Amount']
            .sum().rename('Montant')
    )

    start = f"{year}-{month:02d}-01"
    end   = (pd.to_datetime(start) + pd.offsets.MonthEnd()).date()
    all_days = pd.date_range(start, end, freq='D').date
    daily = daily.reindex(all_days, fill_value=0).reset_index().rename(columns={'index':'Date'})
    fig_daily = px.line(daily, x='Date', y='Montant',
                        title=f"Ventes quotidiennes — {month_name} {year}", markers=True)
    fn_daily = f"daily_{year}_{month:02d}.png"
    fig_daily.write_image(fn_daily, width=1400, height=600, scale=2)

    # catégorie
    cat = df_mois.groupby('Category', as_index=False)['Amount'].sum()\
                 .sort_values('Amount', ascending=False)
    fig_cat = px.bar(cat, x='Category', y='Amount',
                     title=f"CA par catégorie — {month_name} {year}")
    fn_cat = f"cat_{year}_{month:02d}.png"
    fig_cat.write_image(fn_cat, width=1400, height=600, scale=2)

    # canal
    chan = df_mois.groupby('Sales Channel', as_index=False)['Amount'].sum()\
                  .sort_values('Amount', ascending=False)
    fig_chan = px.pie(chan, names='Sales Channel', values='Amount',
                      title=f"Répartition du CA par canal — {month_name} {year}")
    fn_chan = f"chan_{year}_{month:02d}.png"
    fig_chan.write_image(fn_chan, width=1400, height=600, scale=2)

    # top5
    top5 = df_mois.groupby('Style', as_index=False)['Amount'].sum()\
                  .nlargest(5, 'Amount')
    fig_top5 = px.bar(top5, x='Style', y='Amount',
                      title=f"Top 5 styles — {month_name} {year}")
    fn_top5 = f"top5_{year}_{month:02d}.png"
    fig_top5.write_image(fn_top5, width=1400, height=600, scale=2)

    # base64
    return {
        'img_daily': encode_png(fn_daily),
        'img_cat':   encode_png(fn_cat),
        'img_chan':  encode_png(fn_chan),
        'img_top5':  encode_png(fn_top5)
    }

with open("report_template.html", "r", encoding="utf-8") as f:
    tpl_string = f.read()
template = Template(tpl_string)

# Générer et sauvegarder le rapport
def render_and_save(period, kpis, images_b64, template):
    month_name = period.strftime('%B')
    year, month = period.year, period.month
    ca, orders, qty, profit = kpis

    html = template.render(
        month_name=month_name,
        year=year,
        ca_total=f"{ca:,.0f}",
        orders=orders,
        qty=qty,
        profit=f"{profit:,.0f}" if profit is not None else "-",
        **images_b64
    )

    html_path = f"report_{year}_{month:02d}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    pdf_path = html_path.replace(".html", ".pdf")
    pdfkit.from_file(html_path, pdf_path, options=options)
    print(f"✔ Rapport généré pour {month_name} {year} → {pdf_path}")

# Paramètres utilisateur
csv_path = "Amazon Sale Report.csv"
IMG_WIDTH  = 1400
IMG_HEIGHT = 600
IMG_SCALE  = 2

# Options PDFKit (tu peux personnaliser selon ton besoin)
options = {
    'encoding': 'UTF-8',
    'page-size': 'A4',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
}

# Étapes de génération des rapports
df = load_data(csv_path)
periods = get_periods(df)

for period in periods:
    year       = period.year
    month      = period.month
    month_name = period.strftime('%B')

    df_mois = df[df['Date'].dt.to_period('M') == period]
    if df_mois.empty:
        continue

    kpis = compute_kpis(df_mois)

    images_b64 = make_plots(
        df_mois,
        year,
        month,
        month_name,
        width=IMG_WIDTH,
        height=IMG_HEIGHT,
        scale=IMG_SCALE
    )

    render_and_save(period, kpis, images_b64, template)