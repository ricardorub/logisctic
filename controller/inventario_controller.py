import pandas as pd
from flask import jsonify, send_file
from model.models import db, Inventario
import io

def get_all_inventario_json():
    inventario = Inventario.query.all()
    return jsonify([
        {
            'item': i.item,
            'sku': i.sku,
            'producto': i.producto,
            'proveedor': i.proveedor,
            'fecha_pedido': i.fecha_pedido,
            'fecha_recepcion': i.fecha_recepcion,
            'id_pedido_stock': i.id_pedido_stock,
            'ventas': i.ventas,
            'duracion': i.duracion,
            'numero_pedidos': i.numero_pedidos,
            'tiempo_entrega': i.tiempo_entrega,
            'cobertura': i.cobertura,
            'frecuencia': i.frecuencia
        } for i in inventario
    ])

def import_inventario_from_excel(filepath):
    df = pd.read_excel(filepath)
    df.columns = [
        'item', 'sku', 'producto', 'proveedor', 'fecha_pedido', 'fecha_recepcion',
        'id_pedido_stock', 'ventas', 'duracion', 'numero_pedidos',
        'tiempo_entrega', 'cobertura', 'frecuencia'
    ]
    for _, row in df.iterrows():
        new_item = Inventario(**row.to_dict())
        db.session.add(new_item)
    db.session.commit()

def export_inventario_to_excel():
    inventario = Inventario.query.all()
    data = [
        {
            'item': i.item,
            'sku': i.sku,
            'producto': i.producto,
            'proveedor': i.proveedor,
            'fecha_pedido': i.fecha_pedido,
            'fecha_recepcion': i.fecha_recepcion,
            'id_pedido_stock': i.id_pedido_stock,
            'ventas': i.ventas,
            'duracion': i.duracion,
            'numero_pedidos': i.numero_pedidos,
            'tiempo_entrega': i.tiempo_entrega,
            'cobertura': i.cobertura,
            'frecuencia': i.frecuencia
        } for i in inventario
    ]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Inventario')
    writer.close()
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        attachment_filename='inventario.xlsx',
        as_attachment=True
    )

def clear_all_inventario():
    db.session.query(Inventario).delete()
    db.session.commit()
