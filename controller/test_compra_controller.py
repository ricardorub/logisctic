from flask import request, jsonify
from model.models import Compra, Inventario, Test_compra, Test_Inventario, Test_Reposicion
from model.db import db
from datetime import datetime
import random
from sqlalchemy import func

def get_all_test_compras():
    compras = Test_compra.query.all()
    return jsonify([{
        'id': compra.id,
        'compra_id': compra.compra_id,
        'proveedor': compra.proveedor,
        'nombre_producto': compra.nombre_producto,
        'cantidad_proveedor': compra.cantidad_proveedor,
        'precio_unitario': compra.precio_unitario,
        'fecha_compra': compra.fecha_compra.strftime('%Y-%m-%d'),
        'fecha_entrega': compra.fecha_entrega.strftime('%Y-%m-%d'),
        'sku': compra.sku
    } for compra in compras]), 200

def create_test_compra():
    data = request.get_json()
    proveedor = data.get('proveedor')
    nombre_producto = data.get('nombre_producto')
    cantidad_proveedor = data.get('cantidad_proveedor')
    precio_unitario = data.get('precio_unitario')
    fecha_entrega_str = data.get('fecha_entrega')

    if not all([proveedor, nombre_producto, cantidad_proveedor, precio_unitario, fecha_entrega_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    while True:
        compra_id = random.randint(100000, 999999)
        if not Test_compra.query.filter_by(compra_id=compra_id).first():
            break

    existing_item = Test_compra.query.filter_by(nombre_producto=nombre_producto).first()
    if existing_item and existing_item.sku:
        sku = existing_item.sku
    else:
        while True:
            sku = str(random.randint(100000, 999999))
            if not Test_compra.query.filter_by(sku=sku).first():
                break

    new_compra = Test_compra(
        compra_id=compra_id,
        proveedor=proveedor,
        nombre_producto=nombre_producto,
        cantidad_proveedor=int(cantidad_proveedor),
        precio_unitario=float(precio_unitario),
        fecha_compra=datetime.now().date(),
        fecha_entrega=fecha_entrega,
        sku=sku
    )

    try:
        db.session.add(new_compra)
        db.session.commit()
        return jsonify({'message': 'Compra creada exitosamente', 'id': new_compra.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def import_inventario():
    try:
        db.session.query(Test_Inventario).delete()
        
        inventario_to_import = Inventario.query.limit(40).all()
        
        for item in inventario_to_import:
            new_test_inventario = Test_Inventario(
                compra_id=item.compra_id,
                proveedor=item.proveedor,
                nombre_producto=item.nombre_producto,
                sku=item.sku,
                precio_compra=item.precio_compra,
                precio_venta=item.precio_venta,
                cantidad_total=item.cantidad_total,
                fecha_recepcion=item.fecha_recepcion
            )
            db.session.add(new_test_inventario)
            
        db.session.commit()
        return jsonify({'message': '40 items de inventario importados exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def import_compras():
    try:
        db.session.query(Test_compra).delete()
        
        compras_to_import = Compra.query.limit(40).all()
        
        for compra in compras_to_import:
            new_test_compra = Test_compra(
                compra_id=compra.compra_id,
                proveedor=compra.proveedor,
                nombre_producto=compra.nombre_producto,
                cantidad_proveedor=compra.cantidad_proveedor,
                precio_unitario=compra.precio_unitario,
                fecha_compra=compra.fecha_compra,
                fecha_entrega=compra.fecha_entrega,
                sku=compra.sku
            )
            db.session.add(new_test_compra)
            
        db.session.commit()
        return jsonify({'message': '40 compras importadas exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_all_test_reposiciones():
    reposiciones = Test_Reposicion.query.all()
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

def create_test_reposicion():
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

    total_stock = db.session.query(func.sum(Test_Inventario.cantidad_total)).filter_by(nombre_producto=nombre_producto).scalar() or 0

    if total_stock < cantidad:
        return jsonify({'error': 'Cantidad insuficiente en el inventario'}), 400

    inventario_item_to_update = Test_Inventario.query.filter_by(nombre_producto=nombre_producto).order_by(Test_Inventario.cantidad_total.desc()).first()
    
    if not inventario_item_to_update:
         return jsonify({'error': 'Producto no encontrado en el inventario'}), 404

    while True:
        reposicion_id = random.randint(100000, 999999)
        if not Test_Reposicion.query.filter_by(reposicion_id=reposicion_id).first():
            break
    
    new_reposicion = Test_Reposicion(
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

def get_test_productos_disponibles():
    productos_agregados = db.session.query(
        Test_Inventario.nombre_producto,
        Test_Inventario.sku,
        func.sum(Test_Inventario.cantidad_total).label('cantidad_total')
    ).group_by(Test_Inventario.nombre_producto, Test_Inventario.sku).all()
    
    return jsonify([{'nombre_producto': p[0], 'sku': p[1], 'cantidad_total': p[2]} for p in productos_agregados if p[2] > 0]), 200

def update_test_reposicion(id):
    data = request.get_json()
    reposicion = Test_Reposicion.query.get(id)
    if not reposicion:
        return jsonify({'error': 'Reposición no encontrada'}), 404
    
    cantidad_original = reposicion.cantidad
    
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

    total_stock = db.session.query(func.sum(Test_Inventario.cantidad_total)).filter_by(nombre_producto=nombre_producto).scalar() or 0
    
    cantidad_diferencia = cantidad - cantidad_original

    if total_stock < cantidad_diferencia:
        return jsonify({'error': 'Cantidad insuficiente en el inventario para actualizar'}), 400
        
    inventario_item_to_update = Test_Inventario.query.filter_by(nombre_producto=nombre_producto).order_by(Test_Inventario.cantidad_total.desc()).first()

    if not inventario_item_to_update:
        return jsonify({'error': 'Producto no encontrado en el inventario'}), 404

    reposicion.nombre_producto = nombre_producto
    reposicion.cantidad = cantidad
    reposicion.tienda = tienda
    reposicion.fecha_despacho = fecha_despacho
    reposicion.sku = inventario_item_to_update.sku

    try:
        inventario_item_to_update.cantidad_total -= cantidad_diferencia
        db.session.commit()
        return jsonify({'message': 'Reposición actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_test_reposicion(id):
    reposicion = Test_Reposicion.query.get(id)
    if not reposicion:
        return jsonify({'error': 'Reposición no encontrada'}), 404

    inventario_item_to_update = Test_Inventario.query.filter_by(nombre_producto=reposicion.nombre_producto).order_by(Test_Inventario.cantidad_total.desc()).first()

    try:
        if inventario_item_to_update:
            inventario_item_to_update.cantidad_total += reposicion.cantidad
        db.session.delete(reposicion)
        db.session.commit()
        return jsonify({'message': 'Reposición eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_all_test_inventario():
    total_quantities = (
        db.session.query(
            Test_Inventario.nombre_producto,
            func.sum(Test_Inventario.cantidad_total).label('total_quantity')
        )
        .group_by(Test_Inventario.nombre_producto)
        .all()
    )
    
    quantity_map = {item.nombre_producto: item.total_quantity for item in total_quantities}

    latest_items_subquery = (
        db.session.query(
            Test_Inventario.nombre_producto,
            func.max(Test_Inventario.id).label('latest_id')
        )
        .group_by(Test_Inventario.nombre_producto)
        .subquery()
    )

    latest_items = (
        db.session.query(Test_Inventario)
        .join(latest_items_subquery, Test_Inventario.id == latest_items_subquery.c.latest_id)
        .all()
    )

    result = []
    for item in latest_items:
        result.append({
            'nombre_producto': item.nombre_producto,
            'sku': item.sku,
            'precio_compra': item.precio_compra,
            'precio_venta': item.precio_venta,
            'cantidad_total': int(quantity_map.get(item.nombre_producto, 0)),
            'fecha_recepcion': item.fecha_recepcion.strftime('%Y-%m-%d') if item.fecha_recepcion else None
        })
        
    return jsonify(result), 200

def create_test_inventario():
    data = request.get_json()
    compra_id = data.get('compra_id')
    precio_venta = data.get('precio_venta')

    if not all([compra_id, precio_venta]):
        return jsonify({'error': 'Compra ID y Precio Venta son requeridos'}), 400

    compra = Test_compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra ID no encontrado'}), 404

    existing_inventario = Test_Inventario.query.filter_by(compra_id=compra_id).first()
    if existing_inventario:
        return jsonify({'error': 'Este ID de compra ya ha sido añadido al inventario'}), 409

    nuevo_item = Test_Inventario(
        compra_id=compra_id,
        proveedor=compra.proveedor,
        nombre_producto=compra.nombre_producto,
        sku=compra.sku,
        precio_compra=compra.precio_unitario,
        precio_venta=float(precio_venta),
        cantidad_total=compra.cantidad_proveedor,
        fecha_recepcion=datetime.now().date()
    )
    db.session.add(nuevo_item)

    try:
        db.session.commit()
        return jsonify({'message': 'Item de inventario creado exitosamente', 'id': nuevo_item.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ocurrió un error al guardar el item en el inventario'}), 500

def update_test_inventario(nombre_producto):
    data = request.get_json()
    precio_venta = data.get('precio_venta')

    if precio_venta is None:
        return jsonify({'error': 'Precio Venta es requerido'}), 400

    try:
        items_to_update = Test_Inventario.query.filter_by(nombre_producto=nombre_producto).all()
        if not items_to_update:
            return jsonify({'error': 'No se encontraron items para el producto especificado'}), 404

        for item in items_to_update:
            item.precio_venta = float(precio_venta)

        db.session.commit()
        return jsonify({'message': f'Precio de venta actualizado para {nombre_producto}'}), 200
    except (ValueError, TypeError):
        return jsonify({'error': 'Precio de venta debe ser un número válido'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_test_inventario(nombre_producto):
    try:
        items_to_delete = Test_Inventario.query.filter_by(nombre_producto=nombre_producto).all()
        if not items_to_delete:
            return jsonify({'error': 'No se encontraron items para el producto especificado'}), 404

        for item in items_to_delete:
            db.session.delete(item)
        
        db.session.commit()
        return jsonify({'message': f'Items de inventario para {nombre_producto} eliminados exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_available_test_compra_ids():
    inventario_compra_ids = db.session.query(Test_Inventario.compra_id).subquery()
    available_compras = db.session.query(Test_compra.compra_id, Test_compra.nombre_producto)\
        .outerjoin(inventario_compra_ids, Test_compra.compra_id == inventario_compra_ids.c.compra_id)\
        .filter(inventario_compra_ids.c.compra_id == None).all()
    
    return jsonify([{'compra_id': compra[0], 'nombre_producto': compra[1]} for compra in available_compras]), 200

def get_test_compra_details(compra_id):
    compra = Test_compra.query.filter_by(compra_id=compra_id).first()
    if not compra:
        return jsonify({'error': 'Compra no encontrada'}), 404
    return jsonify({
        'proveedor': compra.proveedor,
        'nombre_producto': compra.nombre_producto,
        'precio_unitario': compra.precio_unitario,
        'sku': compra.sku
    }), 200

def update_test_compra(id):
    data = request.get_json()
    compra = Test_compra.query.get(id)
    if not compra:
        return jsonify({'error': 'Compra no encontrada'}), 404

    proveedor = data.get('proveedor')
    nombre_producto = data.get('nombre_producto')
    cantidad_proveedor = data.get('cantidad_proveedor')
    precio_unitario = data.get('precio_unitario')
    fecha_entrega_str = data.get('fecha_entrega')

    if not all([proveedor, nombre_producto, cantidad_proveedor, precio_unitario, fecha_entrega_str]):
        return jsonify({'error': 'Todos los campos son requeridos'}), 400

    try:
        fecha_entrega = datetime.strptime(fecha_entrega_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    if compra.nombre_producto != nombre_producto:
        existing_item = Test_compra.query.filter_by(nombre_producto=nombre_producto).first()
        if existing_item and existing_item.sku:
            compra.sku = existing_item.sku
        else:
            while True:
                sku = str(random.randint(100000, 999999))
                if not Test_compra.query.filter_by(sku=sku).first():
                    compra.sku = sku
                    break

    compra.proveedor = proveedor
    compra.nombre_producto = nombre_producto
    compra.cantidad_proveedor = int(cantidad_proveedor)
    compra.precio_unitario = float(precio_unitario)
    compra.fecha_entrega = fecha_entrega

    try:
        db.session.commit()
        return jsonify({'message': 'Compra actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_test_compra(id):
    compra = Test_compra.query.get(id)
    if not compra:
        return jsonify({'error': 'Compra no encontrada'}), 404

    try:
        db.session.delete(compra)
        db.session.commit()
        return jsonify({'message': 'Compra eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
