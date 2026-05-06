from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Transaction
from app.schemas import TransactionSchema
from app.crud.users import get_user_by_id

async def create_transaction_db(db: AsyncSession, user_id: int, transaction_data: TransactionSchema) -> Transaction:
    new_transaction = Transaction(
        user_id=user_id,
        amount=transaction_data.amount,
        type=transaction_data.type,
        category=transaction_data.category,
        desc=transaction_data.desc
    )

    user = await get_user_by_id(db, user_id)
    if user:
        if new_transaction.type == 'income':
            user.balance += new_transaction.amount 
        else:
            user.balance -= new_transaction.amount

        db.add(new_transaction)
        await db.commit()
        await db.refresh(new_transaction)
        return new_transaction
    else:
        return False

async def delete_transaction_db(db: AsyncSession, user_id: int, transaction_id: int) -> bool:
    query = (
        select(Transaction)
        .where((Transaction.id == transaction_id) & (Transaction.user_id == user_id))
    )
    transaction = (await db.execute(query)).scalar_one_or_none()
    if not transaction:
        return False
    
    user = await get_user_by_id(db, user_id)

    if transaction.type == 'income':
        user.balance -= transaction.amount
    else:
        user.balance += transaction.amount
    
    await db.delete(transaction)
    await db.commit()
    return True