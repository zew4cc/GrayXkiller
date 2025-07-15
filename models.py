#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import hashlib

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)  # Telegram user ID
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    credits = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    premium_type = Column(String(50))  # 'gold', 'platinum', 'diamond'
    premium_expiry = Column(DateTime)
    banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")
    credit_history = relationship("CreditHistory", back_populates="user")

class Plan(Base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    credits = Column(Integer)  # None for unlimited
    duration_days = Column(Integer, nullable=False)
    premium_type = Column(String(50))  # 'gold', 'platinum', 'diamond'
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    transaction_hash = Column(String(255))
    payment_method = Column(String(100))
    amount = Column(Float)
    status = Column(String(50), default='pending')  # 'pending', 'confirmed', 'rejected'
    screenshot_path = Column(String(500))
    admin_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    plan = relationship("Plan")

class CreditHistory(Base):
    __tablename__ = 'credit_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    credits_before = Column(Integer)
    credits_after = Column(Integer)
    credits_used = Column(Integer)
    action = Column(String(100))  # 'chk', 'gen', 'bin', 'kill', 'admin_add', 'purchase'
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="credit_history")

class CheckResult(Base):
    __tablename__ = 'check_results'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_number = Column(String(20))
    gateway = Column(String(100))
    result = Column(String(50))  # 'live', 'dead', 'unknown'
    response_code = Column(String(10))
    response_message = Column(Text)
    processing_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class AdminLog(Base):
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(100))
    target_user_id = Column(BigInteger)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClaimCode(Base):
    __tablename__ = 'claim_codes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(100), unique=True, nullable=False)
    credits = Column(Integer, nullable=False)
    created_by = Column(BigInteger, nullable=False)  # Admin user ID
    claimed_by = Column(BigInteger)  # User ID who claimed it
    claimed_at = Column(DateTime)
    expires_at = Column(DateTime)
    active = Column(Boolean, default=True)
    max_uses = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    
    def init_database():
        """Initialize database tables and default data"""
        Base.metadata.create_all(engine)
        
        session = Session()
        
        # Create default plans
        plans = [
            Plan(name="Gold 8 Days", price=18.0, credits=800, duration_days=8, premium_type="gold", 
                 description="800 credits valid for 8 days"),
            Plan(name="Platinum 8 Days", price=26.0, credits=None, duration_days=8, premium_type="platinum", 
                 description="Unlimited credits for 8 days"),
            Plan(name="Gold 15 Days", price=30.0, credits=1000, duration_days=15, premium_type="gold", 
                 description="1000 credits valid for 15 days"),
            Plan(name="Gold 30 Days", price=40.0, credits=2000, duration_days=30, premium_type="gold", 
                 description="2000 credits valid for 30 days"),
            Plan(name="Diamond 30 Days", price=50.0, credits=None, duration_days=30, premium_type="diamond", 
                 description="Unlimited credits for 30 days")
        ]
        
        for plan in plans:
            existing = session.query(Plan).filter_by(name=plan.name).first()
            if not existing:
                session.add(plan)
        
        session.commit()
        session.close()
    
    def get_session():
        return Session()

else:
    def init_database():
        print("No DATABASE_URL found")
        
    def get_session():
        return None