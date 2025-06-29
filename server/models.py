from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)  # ✅ FIXED
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates='user', cascade="all, delete-orphan")
    serialize_rules = ('-recipes.user',)

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username must not be empty')
        if User.query.filter(User.username == username).first():
            raise ValueError('Username must be unique')
        return username

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is not readable.")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ FIXED

    user = db.relationship('User', back_populates='recipes')
    serialize_rules = ('-user.recipes',)

    @validates('title')
    def validate_title(self, key, title):
        if title:
            return title
        raise ValueError('Title must not be empty')

    @validates('instructions')
    def validate_instruction(self, key, instruction):
        if len(instruction) >= 50:
            return instruction
        raise ValueError('Instruction must be at least 50 characters')
