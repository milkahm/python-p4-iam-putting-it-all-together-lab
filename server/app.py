from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            # use setter to hash password!
            new_user.password_hash = data['password']

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            response = {
                'id': new_user.id,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }
            return response, 201

        except IntegrityError:
            db.session.rollback()
            return {'errors': ['422 Unprocessable Entity']}, 422

        except KeyError:
            return {'errors': ['422 Unprocessable Entity']}, 422


class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        user = User.query.filter_by(id=user_id).first()
        if user:
            response = {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }
            return response, 200

        return {}, 401


class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'message': 'Missing username or password'}, 400

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            response = {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }
            return response, 200

        return {'error': 'Unauthorized'}, 401


class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {'error': 'Unauthorized'}, 401


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.filter_by(user_id=user_id).all()
        recipe_list = [{
            'id': r.id,
            'title': r.title,
            'instructions': r.instructions,
            'minutes_to_complete': r.minutes_to_complete,
            'user_id': r.user_id
        } for r in recipes]

        return recipe_list, 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401

        data = request.get_json()
        try:
            new_recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=user_id
            )
            db.session.add(new_recipe)
            db.session.commit()

            response = {
                'id': new_recipe.id,
                'title': new_recipe.title,
                'instructions': new_recipe.instructions,
                'minutes_to_complete': new_recipe.minutes_to_complete,
                'user_id': new_recipe.user_id
            }
            return response, 201

        except (KeyError, IntegrityError, ValueError):
            db.session.rollback()
            return {'errors': ['422 Unprocessable Entity']}, 422





api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)