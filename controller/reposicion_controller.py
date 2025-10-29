from flask import request, jsonify
from model.models import Reposicion, Inventario
from model.db import db
from datetime import datetime
from sqlalchemy import func
import random

def get_all_reposiciones():
    reposiciones = Reposicion.query.all()
    return jsonify([{
        'id': reposicion.id,
        'reposicion_id': reposicion.reposicion_id,
        'sku': reposicion.sku,
        'nombre_producto': reposicion.nombre_producto,
        'cantidad': reposicion.cantidad,
        'tienda': reposicion.tienda,
        'fecha_reposicion': reposicion.fecha_reposicion.strftime('%Y-%m-%d'),
        'fecha_despacho': reposicion.fecha_despacho.strftime('%Y-%m-%d')
    } for reposicion in reposiciones]), 200

def create_reposicion():
    data = request.get_json()
    nombre_producto = data.get('nombre_producto')
    cantidad = data.get('cantidad')
    tienda = data.get('tienda')
    fecha_despacho_str = data.get('fecha_despacho')

    if not all([nombre_producto, cantidad, tienda, fecha_despacho_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            return jsonify({'error': 'La cantidad debe ser un número positivo.'}), 400
        fecha_despacho = datetime.strptime(fecha_despacho_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'error': 'Formato de fecha o cantidad inválido.'}), 400

    # Calcular el stock total para el producto
    total_stock = db.session.query(func.sum(Inventario.cantidad_total)).filter_by(nombre_producto=nombre_producto).scalar() or 0

    if total_stock < cantidad:
        return jsonify({'error': 'Cantidad insuficiente en el inventario'}), 400

    # Encontrar el item de inventario con la mayor cantidad para restar de allí
    inventario_item_to_update = Inventario.query.filter_by(nombre_producto=nombre_producto).order_by(Inventario.cantidad_total.desc()).first()
    
    if not inventario_item_to_update:
         return jsonify({'error': 'Producto no encontrado en el inventario'}), 404

    # Generate a unique 6-digit reposicion_id
    while True:
        reposicion_id = random.randint(100000, 999999)
        if not Reposicion.query.filter_by(reposicion_id=reposicion_id).first():
            break
    
    new_reposicion = Reposicion(
        reposicion_id=reposicion_id,
        sku=inventario_item_to_update.sku,
        nombre_producto=nombre_producto,
        cantidad=cantidad,
        tienda=tienda,
        fecha_reposicion=datetime.now().date(),
        fecha_despacho=fecha_despacho
    )

    try:
        inventario_item_to_update.cantidad_total -= cantidad
        db.session.add(new_reposicion)
        db.session.commit()
        return jsonify({'message': 'Reposición creada exitosamente', 'id': new_reposicion.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_productos_disponibles():
    # Devuelve la suma total correcta por producto, mostrando solo los que tienen stock.
    productos_agregados = db.session.query(
        Inventario.nombre_producto,
        Inventario.sku,
        func.sum(Inventario.cantidad_total).label('cantidad_total')
    ).group_by(Inventario.nombre_producto, Inventario.sku).all()
    
    return jsonify([{'nombre_producto': p[0], 'sku': p[1], 'cantidad_total': p[2]} for p in productos_agregados if p[2] > 0]), 200
