"""Router del Catálogo de Productos."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..repository import (
    ExistenciasInsuficientes,
    ProductoRepository,
    SkuDuplicado,
    get_repo,
)
from ..schemas import AjusteExistencias, Categoria, ProductoIn, ProductoOut

router = APIRouter(prefix="/productos", tags=["Productos"])

Repo = Annotated[ProductoRepository, Depends(get_repo)]

NO_ENCONTRADO = "Producto no encontrado"


# Ejemplo resuelto: así se traduce una excepción del repositorio a un código HTTP
@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoIn, repo: Repo) -> ProductoOut:
    try:
        return repo.add(data)
    except SkuDuplicado:
        raise HTTPException(status_code=409, detail="El SKU ya existe") from None


# TODO 7: GET /productos con los parámetros de query categoria y solo_disponibles
@router.get("", response_model=list[ProductoOut])
def listar_productos(
    repo: Repo,
    categoria: Categoria | None = None,
    solo_disponibles: bool = False,
) -> list[ProductoOut]:
    return repo.list(categoria, solo_disponibles)


# TODO 8: GET /productos/{producto_id}  (404 si no existe)
@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, repo: Repo) -> ProductoOut:
    producto = repo.get(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return producto


# TODO 9: PUT /productos/{producto_id}  (404 si no existe, 409 si el SKU está en uso)
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, data: ProductoIn, repo: Repo) -> ProductoOut:
    try:
        producto = repo.update(producto_id, data)
    except SkuDuplicado:
        raise HTTPException(status_code=409, detail="El SKU ya existe") from None
    if producto is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return producto


# TODO 10: DELETE /productos/{producto_id}  (204 sin cuerpo, 404 si no existe)
@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, repo: Repo) -> Response:
    if not repo.delete(producto_id):
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# TODO 11: PATCH /productos/{producto_id}/existencias con cuerpo AjusteExistencias
#          (404 si no existe, 409 con detail "Existencias insuficientes")
@router.patch("/{producto_id}/existencias", response_model=ProductoOut)
def ajustar_existencias(producto_id: int, ajuste: AjusteExistencias, repo: Repo) -> ProductoOut:
    try:
        producto = repo.ajustar_existencias(producto_id, ajuste.cantidad)
    except ExistenciasInsuficientes:
        raise HTTPException(status_code=409, detail="Existencias insuficientes") from None
    if producto is None:
        raise HTTPException(status_code=404, detail=NO_ENCONTRADO)
    return producto
