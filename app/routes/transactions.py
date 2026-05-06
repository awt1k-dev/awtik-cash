from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.templating import *
from app.schemas import TransactionSchema
from app.crud.transactions import *
from app.crud.users import *

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/delete/{transaction_id}", name="delete_transaction")
async def delete_transaction(request: Request, transaction_id: int, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return {"ok": False, "message": "Unauthorized"}
    
    result = await delete_transaction_db(db, user_id, transaction_id)
    user = await get_user_with_transactions(db, user_id)
    if result:
        return {
            'ok': True,
            'message': 'Транзакция успешно удалена!',
            'balance': user.balance,
            'transactions_count': len(user.transactions)
        }
    else:
        return {
            "ok": False,
            "message": "Sorry, something went wrong"
        }

@router.post("/create", name="create_transaction")
async def create_transaction(
        request: Request,
        transaction_data: TransactionSchema,
        db: AsyncSession = Depends(get_db)
    ):
    user_id = request.session.get("user_id")
    if not user_id: 
        return {"ok": False, "message": "Unauthorized"}
    
    transaction = await create_transaction_db(db, user_id, transaction_data)

    user_with_transactions = await get_user_with_transactions(db, user_id)

    return {
        'ok': True,
        'message': 'Транзакция успешно добавлена!',
        'balance': user_with_transactions.balance,
        'transactions_count': len(user_with_transactions.transactions),
        'transaction': {
            'id': transaction.id,
            'type': transaction.type,
            'amount': transaction.amount,
            'category': transaction.category,
            'desc': transaction.desc,
            'created_at': transaction.created_at
        }
    }
