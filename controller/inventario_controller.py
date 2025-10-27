from flask import request, jsonify
from model.models import Inventario, Compra
from model.db import db
from datetime import datetime
from sqlalchemy import func

def get_all_inventario():
    # Subquery to get the summed total quantity of received items for each product
    sum_subquery = db.session.query(
        Inventario.nombre_producto,
        func.sum(Inventario.cantidad_total).label('summed_total')
    ).filter(Inventario.status == 'recibido')\
     .group_by(Inventario.nombre_producto).subquery()

    # Main query to join Inventario and the subquery
    inventario_items = db.session.query(
        Inventario,
        sum_subquery.c.summed_total
    ).outerjoin(sum_subquery, Inventario.nombre_producto == sum_subquery.c.nombre_producto)\
     .all()

    # Process the results
    result = []
    for item, summed_total in inventario_items:
        # The total to display is the summed total if the status is "recibido",
        # otherwise it's the item's own quantity.
        display_total = summed_total or 0 if item.status == 'recibido' else item.cantidad_total
        
        result.append({
            'id': item.id,
            'compra_id': item.compra_id,
            'nombre_producto': item.nombre_producto,
            'sku': item.sku,
            'precio_compra': item.precio_compra,
            'precio_venta': item.precio_venta,
            'cantidad_total': display_total,
            'status': item.status,
            'fecha_recepcion': item.fecha_recepcion.strftime('%Y-%m-%d') if item.fecha_recepcion else None
        })
        
    return jsonify(result), 200

def create_inventario():
    data = request.get_json()
    compra_id = data.get('compra_id')
    nombre_producto = data.get('nombre_producto')
    sku = data.get('sku')
    precio_venta = data.get('precio_venta')
    status = data.get('status')

    if not all([compra_id, nombre_producto, sku, precio_venta, status]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    if Inventario.query.filter_by(compra_id=compra_id).first():
        return jsonify({'error': 'Este Compra ID ya ha sido registrado en el inventario.'}), 400
    
    compra = Compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra ID no encontrado'}), 404

    fecha_recepcion = datetime.now().date() if status == 'recibido' else None

    new_item = Inventario(
        compra_id=compra_id,
        nombre_producto=nombre_producto,
        sku=sku,
        precio_compra=compra.precio_unitario,
        precio_venta=float(precio_venta),
        cantidad_total=compra.cantidad_proveedor,
        status=status,
        fecha_recepcion=fecha_recepcion
    )

    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Item de inventario creado exitosamente', 'id': new_item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_productos_inventario():
    productos = Inventario.query.all()
    return jsonify([{
        'nombre_producto': p.nombre_producto,
        'sku': p.sku
    } for p in productos]), 200

def update_inventario(item_id):
    data = request.get_json()
    item = Inventario.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item de inventario no encontrado'}), 404

    compra_id = data.get('compra_id')
    nombre_producto = data.get('nombre_producto')
    sku = data.get('sku')
    precio_venta = data.get('precio_venta')
    status = data.get('status')

    if not all([compra_id, nombre_producto, sku, precio_venta, status]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    # Check if the compra_id is being changed to one that already exists
    if item.compra_id != int(compra_id) and Inventario.query.filter_by(compra_id=compra_id).first():
        return jsonify({'error': 'Este Compra ID ya ha sido registrado en el inventario.'}), 400

    compra = Compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra ID no encontrado'}), 404

    item.compra_id = compra_id
    item.nombre_producto = nombre_producto
    item.sku = sku
    item.precio_compra = compra.precio_unitario
    item.precio_venta = float(precio_venta)
    item.cantidad_total = compra.cantidad_proveedor
    
    if item.status != 'recibido' and status == 'recibido':
        item.fecha_recepcion = datetime.now().date()
    item.status = status


    try:
        db.session.commit()
        return jsonify({'message': 'Item de inventario actualizado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_inventario(item_id):
    item = Inventario.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item de inventario no encontrado'}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item de inventario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
