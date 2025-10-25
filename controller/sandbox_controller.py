from flask import render_template, request, redirect, url_for
from model.models import SandboxItem
from model.db import db

def sandbox():
    items = SandboxItem.query.all()
    return render_template('sandbox.html', items=items)

def add_item():
    item = SandboxItem(
        item=request.form['item'],
        numero_pedidos=request.form['numero_pedidos'],
        duracion_dias=request.form['duracion_dias'],
        frecuencia=request.form['frecuencia'],
        stock_unidades=request.form['stock_unidades'],
        ventas=request.form['ventas'],
        cobertura=request.form['cobertura'],
        fecha_pedido=request.form['fecha_pedido'],
        fecha_entrega=request.form['fecha_entrega'],
        tiempo_entrega=request.form['tiempo_entrega'],
        proveedor=request.form['proveedor']
    )
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('sandbox.sandbox'))

def update_item(item_id):
    item = SandboxItem.query.get(item_id)
    item.item = request.form['item']
    item.numero_pedidos = request.form['numero_pedidos']
    item.duracion_dias = request.form['duracion_dias']
    item.frecuencia = request.form['frecuencia']
    item.stock_unidades = request.form['stock_unidades']
    item.ventas = request.form['ventas']
    item.cobertura = request.form['cobertura']
    item.fecha_pedido = request.form['fecha_pedido']
    item.fecha_entrega = request.form['fecha_entrega']
    item.tiempo_entrega = request.form['tiempo_entrega']
    item.proveedor = request.form['proveedor']
    db.session.commit()
    return redirect(url_for('sandbox.sandbox'))

def delete_item(item_id):
    item = SandboxItem.query.get(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('sandbox.sandbox'))
