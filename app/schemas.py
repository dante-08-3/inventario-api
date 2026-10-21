from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProductoBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=40, examples=["LAP-001"])
    nombre: str = Field(..., min_length=2, max_length=120, examples=["Laptop 14 pulgadas"])
    descripcion: str | None = Field(None, max_length=500, examples=["16 GB RAM, 512 GB SSD"])
    categoria: str = Field("general", max_length=60, examples=["electronica"])
    precio: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2, examples=[15999.90])
    stock: int = Field(0, ge=0, examples=[12])
    stock_minimo: int = Field(5, ge=0, examples=[3])


class ProductoCrear(ProductoBase):
    pass


class ProductoActualizar(BaseModel):
    """Todos los campos son opcionales: solo se cambia lo que mandes."""

    nombre: str | None = Field(None, min_length=2, max_length=120)
    descripcion: str | None = Field(None, max_length=500)
    categoria: str | None = Field(None, max_length=60)
    precio: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)
    stock_minimo: int | None = Field(None, ge=0)


class MovimientoStock(BaseModel):
    tipo: Literal["entrada", "salida"]
    cantidad: int = Field(..., gt=0, examples=[5])


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_bajo: bool
    creado_en: datetime
    actualizado_en: datetime


class PaginaProductos(BaseModel):
    total: int
    pagina: int
    por_pagina: int
    items: list[ProductoOut]


class Resumen(BaseModel):
    total_productos: int
    unidades_en_stock: int
    valor_inventario: Decimal
    productos_stock_bajo: int
    por_categoria: dict[str, int]


class Salud(BaseModel):
    status: Literal["ok", "degradado"]
    version: str
    entorno: str
    base_de_datos: Literal["conectada", "sin conexion"]
