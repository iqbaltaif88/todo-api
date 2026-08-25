from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models
from models import Transactions,Users
from typing import Annotated
from database import engine, SessionLocal
from  fastapi.responses import JSONResponse
from typing import Optional,Literal
from router import auth

from router.auth import get_current_user
from datetime import date as Date


app = FastAPI()


class TransactionBase(BaseModel):
    id:int
    title: str
    amount: float = Field(..., gt=0, description="Amount must be positive")
    type: Literal["income", "expense"]
    category: str
    date: Date


class UpdateTransaction(BaseModel):
    title: Optional[str] = Field(default=None)
    amount: Optional[float] = Field(default=None, gt=0, description="Amount must be positive")
    
    type: Optional[Literal["income", "expense"]] = Field(default=None)
    category: Optional[str] = Field(default=None)
    date: Optional[Date] = Field(default=None)
    
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]







@app.post('/transactions')
def create_transactions(user: user_dependency, db: db_dependency, new_transaction: TransactionBase):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction_model = Transactions(**new_transaction.model_dump(), owner_id=user.get('id'))
    db.add(transaction_model)
    db.commit()

    return JSONResponse(status_code=201, content={'message': 'Transaction created successfully'})



@app.get('/transactions')
def read_transactions(user: user_dependency, db: db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')
   
    return db.query(Transactions).filter(Transactions.owner_id == user.get('id')).all()





@app.get("/transactions/filter")
def filter_transactions(
    user: user_dependency,
    db: db_dependency,
    type: Optional[Literal["income", "expense"]] = None,
    category: Optional[str] = None,
    minimum_amount: Optional[float] = None,
    maximum_amount: Optional[float] = None,
):
    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    # Start with base query filtered by logged-in user
    query = db.query(Transactions).filter(Transactions.owner_id == user.get("id"))

    # Apply optional query parameters dynamically
    if type:
        query = query.filter(Transactions.type == type)

    if category:
        query = query.filter(Transactions.category == category)

    if minimum_amount is not None:
        query = query.filter(Transactions.amount >= minimum_amount)

    if maximum_amount is not None:
        query = query.filter(Transactions.amount <= maximum_amount)

    return query.all()







@app.get('/transactions/{transaction_id}')
def read_specific_transactions(user: user_dependency, db: db_dependency, transaction_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    specific_transaction = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if specific_transaction is not None:
        return specific_transaction
    else:
        raise HTTPException(status_code=404, detail='Transaction not found')





    






 
@app.put('/transactions/{transaction_id}')
def update_transactions(user: user_dependency, db: db_dependency, transaction_id: int, update_transaction: UpdateTransaction):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')

    update_data = update_transaction.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()
    return JSONResponse(status_code=200, content={'message': 'Transaction updated successfully'})







@app.delete('/transactions/{transaction_id}')
def delete_transactions(user: user_dependency, db: db_dependency, transaction_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Failed Authentication')

    transaction = db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail='Transaction not found')

    db.query(Transactions).filter(Transactions.owner_id == user.get('id')).filter(Transactions.id == transaction_id).delete()

    db.commit()
    return JSONResponse(status_code=200, content={'message': 'Transaction deleted successfully'})




