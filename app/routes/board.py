from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from bson import ObjectId

from app.models.board import BoardModel, BoardUpdate, BoardResponse
from app.database.mongodb import board_collection, task_collection, fix_object_id

router = APIRouter(tags=["Boards"], prefix="/boards")

@router.post("/", response_description="Crear un nuevo tablero", response_model=BoardResponse)
async def create_board(board: BoardModel = Body(...)):
    board = jsonable_encoder(board)
    new_board = await board_collection.insert_one(board)
    created_board = await board_collection.find_one({"_id": new_board.inserted_id})
    return fix_object_id(created_board)

@router.get("/", response_description="Listar todos los tableros", response_model=List[BoardResponse])
async def list_boards():
    boards = await board_collection.find().to_list(1000)
    return fix_object_id(boards)

@router.get("/{id}", response_description="Obtener un tablero por ID", response_model=BoardResponse)
async def get_board(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
    
    board = await board_collection.find_one({"_id": ObjectId(id)})
    if board is None:
        raise HTTPException(status_code=404, detail=f"Tablero con ID {id} no encontrado")
    
    return fix_object_id(board)

@router.put("/{id}", response_description="Actualizar un tablero", response_model=BoardResponse)
async def update_board(id: str, board: BoardUpdate = Body(...)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
    
    # Excluir campos None/null
    board_data = {k: v for k, v in board.model_dump(exclude_unset=True).items() if v is not None}
    
    if not board_data:
        raise HTTPException(status_code=400, detail="Se debe proporcionar al menos un campo para actualizar")

    result = await board_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": board_data}
    )

    if result.modified_count == 0:
        # Verificar si el documento existe
        if (await board_collection.find_one({"_id": ObjectId(id)})) is None:
            raise HTTPException(status_code=404, detail=f"Tablero con ID {id} no encontrado")
    
    updated_board = await board_collection.find_one({"_id": ObjectId(id)})
    return fix_object_id(updated_board)

@router.delete("/{id}", response_description="Eliminar un tablero")
async def delete_board(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
    
    # Eliminar el tablero
    board_delete_result = await board_collection.delete_one({"_id": ObjectId(id)})
    
    if board_delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Tablero con ID {id} no encontrado")
    
    # Eliminar todas las tareas asociadas al tablero
    await task_collection.delete_many({"board_id": ObjectId(id)})
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": f"Tablero con ID {id} y todas sus tareas eliminadas correctamente"}
    )