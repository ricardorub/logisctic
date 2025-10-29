from flask import request, redirect, url_for, render_template, send_file
from model.models import CrudItem
from model.db import db
import pandas as pd
from io import BytesIO
from datetime import datetime

def get_items():
    items = CrudItem.query.all()
    return render_template('crud.html', items=items)

def _parse_date(date_string):
    if date_string:
        try:
            return datetime.strptime(date_string, '%Y-%m-%d').date()
        except ValueError:
            return None
    return None

def _parse_float(float_string):
    if float_string:
        try:
            return float(float_string)
        except (ValueError, TypeError):
            return None
    return None

def _parse_int(int_string):
    if int_string:
        try:
            return int(int_string)
        except (ValueError, TypeError):
            return None
    return None

def add_item():
    new_item = CrudItem(
        sku=request.form.get('sku'),
        proveedor=request.form.get('proveedor'),
        producto=request.form.get('producto'),
        stock=_parse_int(request.form.get('stock')),
        fecha_pedido=_parse_date(request.form.get('fecha_pedido')),
        fecha_recepcion=_parse_date(request.form.get('fecha_recepcion')),
        id_pedido=request.form.get('id_pedido'),
        ventas=_parse_float(request.form.get('ventas')),
        numero_pedidos=_parse_int(request.form.get('numero_pedidos')),
        duracion=_parse_int(request.form.get('duracion'))
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('crud.get_items'))

def update_item(item_id):
    item = CrudItem.query.get(item_id)
    if item:
        item.sku = request.form.get('sku')
        item.proveedor = request.form.get('proveedor')
        item.producto = request.form.get('producto')
        item.stock = _parse_int(request.form.get('stock'))
        item.fecha_pedido = _parse_date(request.form.get('fecha_pedido'))
        item.fecha_recepcion = _parse_date(request.form.get('fecha_recepcion'))
        item.id_pedido = request.form.get('id_pedido')
        item.ventas = _parse_float(request.form.get('ventas'))
        item.numero_pedidos = _parse_int(request.form.get('numero_pedidos'))
        item.duracion = _parse_int(request.form.get('duracion'))
        db.session.commit()
    return redirect(url_for('crud.get_items'))

def delete_item(item_id):
    item = CrudItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('crud.get_items'))

def export_excel():
    items = CrudItem.query.all()
    data = {
        'SKU': [item.sku for item in items],
        'Proveedor': [item.proveedor for item in items],
        'Producto': [item.producto for item in items],
        'Stock': [item.stock for item in items],
        'Fecha de Pedido': [item.fecha_pedido for item in items],
        'Fecha de Recepción': [item.fecha_recepcion for item in items],
        'ID del Pedido': [item.id_pedido for item in items],
        'Ventas': [item.ventas for item in items],
        'Numero de Pedidos': [item.numero_pedidos for item in items],
        'Duracion': [item.duracion for item in items]
    }
    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='report.xlsx'
    )
