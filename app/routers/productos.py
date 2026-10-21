from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Producto
from app.schemas import (
    MovimientoStock,
    PaginaProductos,
    ProductoActualizar,
    ProductoCrear,
    ProductoOut,
    Resumen,
)
from app.security import verificar_api_key

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"], dependencies=[Depends(verificar_api_key)])


def _out(p: Producto) -> ProductoOut:
    return ProductoOut.model_validate({**p.__dict__, "stock_bajo": p.stock <= p.stock_minimo})


def _obtener(db: Session, producto_id: int) -> Producto:
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Producto {producto_id} no existe")
    return producto


@router.get("", response_model=PaginaProductos, summary="Listar productos")
def listar(
    q: str | None = Query(None, description="Busca en nombre o SKU"),
    categoria: str | None = None,
    solo_stock_bajo: bool = False,
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = select(Producto)
    if q:
        like = f"%{q}%"
        consulta = consulta.where(or_(Producto.nombre.ilike(like), Producto.sku.ilike(like)))
    if categoria:
        consulta = consulta.where(Producto.categoria == categoria)
    if solo_stock_bajo:
        consulta = consulta.where(Producto.stock <= Producto.stock_minimo)

    total = db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    items = db.scalars(
        consulta.order_by(Producto.id).offset((pagina - 1) * por_pagina).limit(por_pagina)
    ).all()
    return PaginaProductos(total=total, pagina=pagina, por_pagina=por_pagina, items=[_out(p) for p in items])


@router.get("/resumen", response_model=Resumen, summary="Resumen del inventario")
def resumen(db: Session = Depends(get_db)):
    productos = db.scalars(select(Producto)).all()
    por_categoria: dict[str, int] = {}
    for p in productos:
        por_categoria[p.categoria] = por_categoria.get(p.categoria, 0) + 1
    return Resumen(
        total_productos=len(productos),
        unidades_en_stock=sum(p.stock for p in productos),
        valor_inventario=sum((p.precio * p.stock for p in productos), Decimal("0")),
        productos_stock_bajo=sum(1 for p in productos if p.stock <= p.stock_minimo),
        por_categoria=por_categoria,
    )


@router.get("/{producto_id}", response_model=ProductoOut, summary="Ver un producto")
def ver(producto_id: int, db: Session = Depends(get_db)):
    return _out(_obtener(db, producto_id))


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED, summary="Crear producto")
def crear(datos: ProductoCrear, db: Session = Depends(get_db)):
    if db.scalar(select(Producto).where(Producto.sku == datos.sku)):
        raise HTTPException(status.HTTP_409_CONFLICT, f"Ya existe un producto con SKU {datos.sku}")
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return _out(producto)


@router.patch("/{producto_id}", response_model=ProductoOut, summary="Actualizar producto")
def actualizar(producto_id: int, datos: ProductoActualizar, db: Session = Depends(get_db)):
    producto = _obtener(db, producto_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return _out(producto)


@router.post("/{producto_id}/movimientos", response_model=ProductoOut, summary="Entrada o salida de stock")
def mover_stock(producto_id: int, mov: MovimientoStock, db: Session = Depends(get_db)):
    producto = _obtener(db, producto_id)
    if mov.tipo == "salida" and mov.cantidad > producto.stock:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Stock insuficiente: hay {producto.stock}, se pidieron {mov.cantidad}",
        )
    producto.stock += mov.cantidad if mov.tipo == "entrada" else -mov.cantidad
    db.commit()
    db.refresh(producto)
    return _out(producto)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar producto")
def eliminar(producto_id: int, db: Session = Depends(get_db)):
    db.delete(_obtener(db, producto_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
