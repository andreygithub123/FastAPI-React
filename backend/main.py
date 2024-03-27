from fastapi import FastAPI,HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

origins = [
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

class TransactionBase(BaseModel):
    amount: float
    category: str
    description:str
    is_income:bool
    date:str

class TransactionModel(TransactionBase):
    id:int
    
    class Config:
        form_attributes=True


#make sure that our connection string only opens up when the request comes in and then close it when the request is complete
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependendcy = Annotated[Session,Depends(get_db)]

models.Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to the Transactions API!"}


@app.get("/transactions/",response_model=list[TransactionModel])
async def read_transactions(db:db_dependendcy,skip: int=0, limit:int = 100):
    transactions=db.query(models.Transaction).offset(skip).limit(limit).all()
    return transactions

@app.post("/transactions/",response_model=TransactionModel)
async def create_transaction(transaction:TransactionBase,db:db_dependendcy):
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction