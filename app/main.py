from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from pydantic import BaseModel
from typing import Optional

from .database import SessionLocal, engine, Base
from .models import Tree, User
from .schemas import TreeCreate, TreeUpdate, UserCreate, UserLogin, Token
from .auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tree Monitoring API")


# ==========================
# Database Dependency
# ==========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================
# AUTHENTICATION ENDPOINTS
# ==========================

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    db_user = User(
        username=user.username,
        password_hash=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()

    return {"message": "User registered successfully"}


@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.username == user.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        user.password,
        db_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": db_user.username}
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ==========================
# TREE ENDPOINTS
# ==========================

@app.post("/trees")
def add_tree(
    tree: TreeCreate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    db_tree = Tree(**tree.dict())

    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)

    return db_tree


@app.get("/trees")
def get_trees(
    species: str = None,
    health: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Tree)

    if species:
        query = query.filter(
            Tree.species_name == species
        )

    if health:
        query = query.filter(
            Tree.health_status == health
        )

    return query.all()


@app.put("/trees/{tree_id}")
def update_tree(
    tree_id: int,
    update: TreeUpdate,
    db: Session = Depends(get_db),
    user=Depends(verify_token)
):
    tree = db.query(Tree).filter(
        Tree.id == tree_id
    ).first()

    if not tree:
        raise HTTPException(
            status_code=404,
            detail="Tree not found"
        )

    tree.health_status = update.health_status

    db.commit()
    db.refresh(tree)

    return {
        "message": "Updated successfully",
        "tree": tree
    }


@app.get("/trees/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Tree).count()

    species_counts = db.query(
        Tree.species_name,
        func.count(Tree.id)
    ).group_by(
        Tree.species_name
    ).all()

    health_counts = db.query(
        Tree.health_status,
        func.count(Tree.id)
    ).group_by(
        Tree.health_status
    ).all()

    good_count = db.query(Tree).filter(
        Tree.health_status == "Good"
    ).count()

    percentage = (
        (good_count / total) * 100
        if total > 0 else 0
    )

    return {
        "species_counts": dict(species_counts),
        "health_counts": dict(health_counts),
        "good_health_percentage": round(percentage, 2)
    }