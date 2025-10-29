from flask import request, jsonify
from model.models import Reposicion, Inventario
from model.db import db
from datetime import datetime
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
        fecha_despacho = datetime.strptime(fecha_despacho_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha o cantidad inválido.'}), 400

    inventario_item = Inventario.query.filter_by(nombre_producto=nombre_producto).first()
    if not inventario_item:
        return jsonify({'error': 'Producto no encontrado en el inventario'}), 404

    if inventario_item.cantidad_total < cantidad:
        return jsonify({'error': 'Cantidad insuficiente en el inventario'}), 400

    # Generate a unique 6-digit reposicion_id
    while True:
        reposicion_id = random.randint(100000, 999999)
        if not Reposicion.query.filter_by(reposicion_id=reposicion_id).first():
            break
    
    new_reposicion = Reposicion(
        reposicion_id=reposicion_id,
        sku=inventario_item.sku,
        nombre_producto=nombre_producto,
        cantidad=cantidad,
        tienda=tienda,
        fecha_reposicion=datetime.now().date(),
        fecha_despacho=fecha_despacho
    )

    try:
        inventario_item.cantidad_total -= cantidad
        db.session.add(new_reposicion)
        db.session.commit()
        return jsonify({'message': 'Reposición creada exitosamente', 'id': new_reposicion.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_productos_disponibles():
    productos = Inventario.query.with_entities(Inventario.nombre_producto, Inventario.sku, Inventario.cantidad_total).all()
    return jsonify([{'nombre_producto': p[0], 'sku': p[1], 'cantidad_total': p[2]} for p in productos]), 200
