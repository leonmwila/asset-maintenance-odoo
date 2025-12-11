#!/usr/bin/env python3
import xmlrpc.client

url = "http://localhost:3000"
db = "asset_maintenance_db"
username = "Admin"
password = "Zikomo@2025"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search for company-related menus
menus = models.execute_kw(db, uid, password,
    'ir.ui.menu', 'search_read',
    [[['name', 'ilike', 'compan']]],
    {'fields': ['name', 'id']})

print("Company-related menus:")
for menu in menus:
    # Get XML ID
    data = models.execute_kw(db, uid, password,
        'ir.model.data', 'search_read',
        [[['model', '=', 'ir.ui.menu'], ['res_id', '=', menu['id']]]],
        {'fields': ['complete_name', 'module', 'name']})
    
    xml_id = f"{data[0]['module']}.{data[0]['name']}" if data else "No XML ID"
    print(f"  {menu['name']} -> {xml_id}")
