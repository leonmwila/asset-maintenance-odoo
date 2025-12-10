{
    'name': 'Company Extension',
    'version': '1.11',
    'category': 'Base',
    'summary': 'Adds Province, District, GRZ Number, Company Type, and Ministry terminology',
    'depends': ['base','stock', 'product', 'repair', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/program_project.xml',
        'views/res_company_views.xml',
        'views/stock_production_lot_views.xml',
        'views/product_category_views.xml',
        'views/product_category_2_views.xml',
        'views/programs_and_projects_views.xml',
        'views/technician_menus.xml',
        'views/repair_order_views.xml',
        'views/ministry_terminology.xml',
        'data/province_district_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'company_extension/static/src/scss/custom_theme.scss',
            'company_extension/static/src/js/terminology_override.js',
        ],
    },
    'installable': True,
    'application': True,
}
