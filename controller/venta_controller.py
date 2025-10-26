from flask import request, jsonify
from model.models import Venta
from model.db import db
from datetime import datetime

def get_all_ventas():
    ventas = Venta.query.all()
    return jsonify([{
        'id': venta.id,
        'sku': venta.sku,
        'nombre_producto': venta.nombre_producto,
        'cantidad_vendida': venta.cantidad_vendida,
        'precio_unidad': venta.precio_unidad,
        'fecha_pedido': venta.fecha_pedido.strftime('%Y-%m-%d'),
        'fecha_recepcion': venta.fecha_recepcion.strftime('%Y-%m-%d')
    } for venta in ventas]), 200

def create_venta():
    data = request.get_json()
    sku = data.get('sku')
    nombre_producto = data.get('nombre_producto')
    cantidad_vendida = data.get('cantidad_vendida')
    precio_unidad = data.get('precio_unidad')
    fecha_pedido_str = data.get('fecha_pedido')
    fecha_recepcion_str = data.get('fecha_recepcion')

    if not all([sku, nombre_producto, cantidad_vendida, precio_unidad, fecha_pedido_str, fecha_recepcion_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_pedido = datetime.strptime(fecha_pedido_str, '%Y-%m-%d').date()
        fecha_recepcion = datetime.strptime(fecha_recepcion_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    new_venta = Venta(
        sku=sku,
        nombre_producto=nombre_producto,
        cantidad_vendida=int(cantidad_vendida),
        precio_unidad=float(precio_unidad),
        fecha_pedido=fecha_pedido,
        fecha_recepcion=fecha_recepcion
    )

    try:
        db.session.add(new_venta)
        db.session.commit()
        return jsonify({'message': 'Venta creada exitosamente', 'id': new_venta.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_venta(venta_id):
    data = request.get_json()
    venta = Venta.query.get(venta_id)
    if not venta:
        return jsonify({'error': 'Venta no encontrada'}), 404

    sku = data.get('sku')
    nombre_producto = data.get('nombre_producto')
    cantidad_vendida = data.get('cantidad_vendida')
    precio_unidad = data.get('precio_unidad')
    fecha_pedido_str = data.get('fecha_pedido')
    fecha_recepcion_str = data.get('fecha_recepcion')

    if not all([sku, nombre_producto, cantidad_vendida, precio_unidad, fecha_pedido_str, fecha_recepcion_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_pedido = datetime.strptime(fecha_pedido_str, '%Y-%m-%d').date()
        fecha_recepcion = datetime.strptime(fecha_recepcion_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    venta.sku = sku
    venta.nombre_producto = nombre_producto
    venta.cantidad_vendida = int(cantidad_vendida)
    venta.precio_unidad = float(precio_unidad)
    venta.fecha_pedido = fecha_pedido
    venta.fecha_recepcion = fecha_recepcion

    try:
        db.session.commit()
        return jsonify({'message': 'Venta actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_venta(venta_id):
    venta = Venta.query.get(venta_id)
    if not venta:
        return jsonify({'error': 'Venta no encontrada'}), 404

    try:
        db.session.delete(venta)
        db.session.commit()
        return jsonify({'message': 'Venta eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
