from flask import request, jsonify
from model.models import Inventario, Compra
from model.db import db
from datetime import datetime
from sqlalchemy import func
import random

def get_all_inventario():
    # Subquery to sum the quantity for each product from all inventory items
    sum_subquery = db.session.query(
        Inventario.nombre_producto,
        func.sum(Inventario.cantidad_total).label('summed_total')
    ).group_by(Inventario.nombre_producto).subquery()

    # Query inventory items and join with the summed quantities
    inventario_items = db.session.query(
        Inventario,
        sum_subquery.c.summed_total
    ).join(sum_subquery, Inventario.nombre_producto == sum_subquery.c.nombre_producto).all()

    result = []
    for item, summed_total in inventario_items:
        result.append({
            'id': item.id,
            'compra_id': item.compra_id,
            'proveedor': item.proveedor,
            'nombre_producto': item.nombre_producto,
            'sku': item.sku,
            'precio_compra': item.precio_compra,
            'precio_venta': item.precio_venta,
            'cantidad_total': summed_total,
            'fecha_recepcion': item.fecha_recepcion.strftime('%Y-%m-%d') if item.fecha_recepcion else None
        })
        
    return jsonify(result), 200

def create_inventario():
    data = request.get_json()
    compra_id = data.get('compra_id')
    precio_venta = data.get('precio_venta')

    if not all([compra_id, precio_venta]):
        return jsonify({'error': 'Compra ID y Precio Venta son requeridos'}), 400

    if Inventario.query.filter_by(compra_id=compra_id).first():
        return jsonify({'error': 'Este Compra ID ya ha sido registrado en el inventario.'}), 400
    
    compra = Compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra ID no encontrado'}), 404

    # Generate or retrieve SKU
    existing_item = Inventario.query.filter_by(nombre_producto=compra.nombre_producto).first()
    if existing_item:
        sku = existing_item.sku
    else:
        while True:
            sku = str(random.randint(100000, 999999))
            if not Inventario.query.filter_by(sku=sku).first():
                break
    
    new_item = Inventario(
        compra_id=compra_id,
        proveedor=compra.proveedor,
        nombre_producto=compra.nombre_producto,
        sku=sku,
        precio_compra=compra.precio_unitario,
        precio_venta=float(precio_venta),
        cantidad_total=compra.cantidad_proveedor, # Storing the individual quantity
        fecha_recepcion=datetime.now().date()
    )

    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Item de inventario creado exitosamente', 'id': new_item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_productos_inventario():
    productos = Inventario.query.distinct(Inventario.nombre_producto).all()
    return jsonify([{
        'nombre_producto': p.nombre_producto,
        'sku': p.sku
    } for p in productos]), 200

def update_inventario(item_id):
    data = request.get_json()
    item = Inventario.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item de inventario no encontrado'}), 404

    precio_venta = data.get('precio_venta')
    if precio_venta is None:
        return jsonify({'error': 'Precio Venta es requerido'}), 400
    
    try:
        item.precio_venta = float(precio_venta)
        db.session.commit()
        return jsonify({'message': 'Item de inventario actualizado exitosamente'}), 200
    except (ValueError, TypeError):
        return jsonify({'error': 'Precio de venta debe ser un número válido'}), 400
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
