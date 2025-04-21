from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import shutil
import os

from app.core.config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from app.core.secure import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_superuser, get_db
)
from app.core.cache import cache, invalidate_cache
from app.utils.logger import logger
from app.models.user import User
from app.models.products import Product
from app.schemas.user import UserCreate, UserRead
from app.schemas.products import ProductCreate, ProductRead, ProductUpdate

app = FastAPI()

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user with email: {user.email}")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"Registration failed: email {user.email} already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User {user.email} registered successfully")
    return db_user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    logger.info(f"Login successful for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/products/", response_model=ProductRead)
@cache(ttl=3600)
async def create_product(
    product: ProductCreate,
    image: UploadFile = File(None),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    logger.info(f"Creating product: {product.name}")
    if image:
        if image.size > MAX_FILE_SIZE:
            logger.warning(f"Image too large for product: {product.name}")
            raise HTTPException(status_code=400, detail="File too large")
        
        file_extension = image.filename.split(".")[-1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file type for product: {product.name}")
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        file_path = os.path.join(UPLOAD_DIR, f"{product.name}_{image.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        product.image_url = file_path
        logger.info(f"Image uploaded for product: {product.name}")

    db_product = Product(**product.dict(), owner_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    invalidate_cache("get_products:*")
    
    logger.info(f"Product created successfully: {product.name}")
    return db_product

@app.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    logger.info(f"Attempting to delete product with ID: {product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        logger.warning(f"Product not found: {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.owner_id != current_user.id:
        logger.warning(f"Permission denied for deleting product: {product_id}")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if product.image_url and os.path.exists(product.image_url):
        os.remove(product.image_url)
        logger.info(f"Image deleted for product: {product_id}")
    
    db.delete(product)
    db.commit()
    
    invalidate_cache("get_products:*")
    
    logger.info(f"Product deleted successfully: {product_id}")
    return {"message": "Product deleted successfully"}

@app.post("/orders/")
async def create_order(
    product_ids: List[int],
    quantities: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Creating order for user: {current_user.email}")
    if len(product_ids) != len(quantities):
        logger.warning("Invalid order request: product IDs and quantities mismatch")
        raise HTTPException(status_code=400, detail="Product IDs and quantities must match")
    
    total_amount = 0
    for product_id, quantity in zip(product_ids, quantities):
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            logger.warning(f"Product not found in order: {product_id}")
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        if product.quantity < quantity:
            logger.warning(f"Insufficient quantity for product: {product_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Not enough quantity for product {product.name}"
            )
        
        total_amount += product.price * quantity
        product.quantity -= quantity
    
    db.commit()
    
    invalidate_cache("get_products:*")
    
    logger.info(f"Order created successfully for user: {current_user.email}")
    return {"message": "Order created successfully", "total_amount": total_amount}

