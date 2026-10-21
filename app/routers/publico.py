"""Consultas públicas (solo lectura): se pueden abrir directo en el navegador.

Responden con el formato {"data": ...}. Crear, editar y borrar siguen en
/api/v1/productos y requieren la API key.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Producto

router = APIRouter(prefix="/api/productos", tags=["Consulta pública"])


def _a_dict(p: Producto) -> dict:
    return {
        "id": str(p.id),
        "sku": p.sku,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "categoria": p.categoria,
        "precio": float(p.precio),
        "stock": p.stock,
        "stock_minimo": p.stock_minimo,
        "stock_bajo": p.stock <= p.stock_minimo,
        "created_at": p.creado_en.isoformat() if p.creado_en else None,
    }


@router.get("", summary="Ver todos los productos")
def todos(db: Session = Depends(get_db)):
    productos = db.scalars(select(Producto).order_by(Producto.id)).all()
    return {"data": [_a_dict(p) for p in productos], "total": len(productos)}


@router.get("/{producto_id}", summary="Ver un producto por id")
def uno(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Producto {producto_id} no existe")
    return {"data": _a_dict(producto)}
