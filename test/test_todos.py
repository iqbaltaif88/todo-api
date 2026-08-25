from test.test_main import client
from main import app
from fastapi import status
from router.auth import get_current_user
from database import SessionLocal
from models import Transactions
from datetime import date


def override_get_current_user():
    return {
        'id': 1,
        'username': 'testuser'
    }


def test_transaction():

    db = SessionLocal()

    # remove old test data if its exist
    db.query(Transactions).filter(Transactions.id == 99).delete()

    transaction = Transactions(
        id = 99,
        title = 'Testing',
        amount = 50,
        type = 'income',
        category = 'Food',
        date = date(2025, 1, 1),
        owner_id = 1,
            )

    db.add(transaction)
    db.commit()


app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_transactions():
    response = client.get('/transactions')
    assert response.status_code == status.HTTP_200_OK


def test_read_specific_transactions():
    response = client.get('/transactions/99')
    assert response.status_code == status.HTTP_200_OK




def test_create_transaction():

    db = SessionLocal()
    # remove old test data if its exist
    db.query(Transactions).filter(Transactions.id == 0).delete()
    db.commit()

    request_data = {
    "id": 0,
    "title": "string",
    "amount": 1,
    "type": "income",
    "category": "string",
    "date": "2026-08-25"
    }
    response = client.post('/transactions', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {'message' : 'Transaction created successfully'}


def test_update_transaction():

    request_data = {
        "title": "meew"
    }
    response = client.put('/transactions/99', json=request_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message' : 'Transaction updated successfully'}

def test_delete_transaction():

    response = client.delete('/transactions/99')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message' : 'Transaction deleted successfully'}