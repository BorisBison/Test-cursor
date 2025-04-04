from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_code = Column(String)
    gender = Column(String)
    age = Column(Integer)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Database:
    def __init__(self):
        self.engine = create_engine('sqlite:///bot_database.db')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_or_update_user(self, user_data):
        user = self.session.query(User).filter_by(user_id=user_data['user_id']).first()
        
        if user:
            # Обновляем существующего пользователя
            for key, value in user_data.items():
                setattr(user, key, value)
            user.last_activity = datetime.utcnow()
        else:
            # Создаем нового пользователя
            user = User(**user_data)
            self.session.add(user)
        
        self.session.commit()
        return user

    def update_user_language(self, user_id, language):
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.language_code = language
            self.session.commit()

    def get_user_stats(self):
        total_users = self.session.query(User).count()
        active_users = self.session.query(User).filter_by(is_active=True).count()
        return {
            'total_users': total_users,
            'active_users': active_users
        }

    def get_all_users(self):
        return self.session.query(User).all()

    def export_users_to_csv(self, filename='users_export.csv'):
        import pandas as pd
        users = self.session.query(User).all()
        data = [{
            'user_id': user.user_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code,
            'gender': user.gender,
            'age': user.age,
            'country': user.country,
            'created_at': user.created_at,
            'last_activity': user.last_activity,
            'is_active': user.is_active
        } for user in users]
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename 
