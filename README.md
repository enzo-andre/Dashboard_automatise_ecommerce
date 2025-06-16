# Dashboard & Rapports Automatisés E-commerce

Un pipeline Python de bout en bout pour générer automatiquement des rapports mensuels PDF à partir d’un dataset de ventes e-commerce (Amazon Sale Report).

## Fonctionnalités

- Lecture et nettoyage du fichier CSV
- Calcul des KPI clés :  
  - Chiffre d’affaires (CA)  
  - Nombre de commandes  
  - Quantité vendue  
  - Profit (si présence de la colonne)  
- Visualisations :  
  - Courbe jour par jour (avec jours à zéro si pas de ventes)  
  - CA par catégorie (bar chart)  
  - Répartition du CA par canal de vente (camembert)  
  - Top 5 des styles (bar chart)  
- Export graphique en haute résolution (PNG / SVG)  
- Insertion inline (Base64) dans un template Jinja2  
- Génération de rapports HTML puis conversion en PDF via wkhtmltopdf  
- Boucle automatique sur tous les mois présents dans les données  

## 📁 Structure du projet

```text
mon-dashboard-ecommerce/
├── data/
│   └── Amazon Sale Report.zip
│      └── Amazon Sale Report.csv           
├── templates/
│   └── report_template.html             # Template Jinja du rapport
├── scripts/
│   └── Rapport_automatise_ecommerce.py
│   └── Rapport_automatise_ecommerce.ipynb
├── reports/
│   └── 2022/                            
│       ├── report_2022_03.pdf
│       └── report_2022_04.pdf
│       ├── report_2022_05.pdf
│       └── report_2022_06.pdf
├── requirements.txt                 
└── README.md                            
