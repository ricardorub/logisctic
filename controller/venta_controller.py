from flask import request, jsonify
from model.models import Venta, Inventario
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
        'monto_total': venta.monto_total,
        'fecha_pedido': venta.fecha_pedido.strftime('%Y-%m-%d'),
        'fecha_recepcion': venta.fecha_recepcion.strftime('%Y-%m-%d')
    } for venta in ventas]), 200

def create_venta():
    data = request.get_json()
    sku = data.get('sku')
    nombre_producto = data.get('nombre_producto')
    cantidad_vendida = data.get('cantidad_vendida')
    fecha_recepcion_str = data.get('fecha_recepcion')

    if not all([sku, nombre_producto, cantidad_vendida, fecha_recepcion_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_recepcion = datetime.strptime(fecha_recepcion_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    inventario_item = Inventario.query.filter_by(sku=sku).first()
    if not inventario_item:
        return jsonify({'error': 'Inventario no encontrado para el SKU proporcionado'}), 404

    if inventario_item.cantidad_total < int(cantidad_vendida):
        return jsonify({'error': 'No hay suficiente stock para realizar la venta'}), 400

    inventario_item.cantidad_total -= int(cantidad_vendida)
    
    precio_unidad = inventario_item.precio_compra
    monto_total = int(cantidad_vendida) * precio_unidad

    new_venta = Venta(
        sku=sku,
        nombre_producto=nombre_producto,
        cantidad_vendida=int(cantidad_vendida),
        precio_unidad=precio_unidad,
        monto_total=monto_total,
        fecha_pedido=datetime.now().date(),
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

    cantidad_vendida_nueva = data.get('cantidad_vendida')
    fecha_recepcion_str = data.get('fecha_recepcion')

    if not all([cantidad_vendida_nueva, fecha_recepcion_str]):
        return jsonify({'error': 'La cantidad vendida y la fecha de recepción son requeridas'}), 400

    try:
        fecha_recepcion = datetime.strptime(fecha_recepcion_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    inventario_item = Inventario.query.filter_by(sku=venta.sku).first()
    if not inventario_item:
        return jsonify({'error': 'Inventario no encontrado para el SKU de la venta'}), 404

    diferencia_cantidad = int(cantidad_vendida_nueva) - venta.cantidad_vendida
    if inventario_item.cantidad_total < diferencia_cantidad:
        return jsonify({'error': 'No hay suficiente stock para actualizar la venta'}), 400

    inventario_item.cantidad_total -= diferencia_cantidad
    venta.cantidad_vendida = int(cantidad_vendida_nueva)
    venta.monto_total = venta.cantidad_vendida * venta.precio_unidad
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

    inventario_item = Inventario.query.filter_by(sku=venta.sku).first()
    if inventario_item:
        inventario_item.cantidad_total += venta.cantidad_vendida

    try:
        db.session.delete(venta)
        db.session.commit()
        return jsonify({'message': 'Venta eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
