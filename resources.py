from flask import jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from flask_restful import Resource, reqparse

from models import UserModel, RevokedTokenModel

parser = reqparse.RequestParser()
parser.add_argument('username', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}, 200, {'Access-Control-Allow-Origin': '*'}

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password']),
            role=data['role']
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200, {'Access-Control-Allow-Origin': '*'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}, 200, {'Access-Control-Allow-Origin': '*'}

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['username'])
            refresh_token = create_refresh_token(identity=data['username'])

            return {
                'id': current_user.id,
                'firstName': current_user.firstname,
                'lastName': current_user.lastname,
                'username': current_user.username,
                'role': current_user.role,
                'jwtToken': access_token,
                'jwtRefreshToken': refresh_token
            }, 200, {'Access-Control-Allow-Origin': '*'}
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}, 200, {'Access-Control-Allow-Origin': '*'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}, 200, {'Access-Control-Allow-Origin': '*'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {
            'jwtRefreshToken': access_token
        }, 200, {'Access-Control-Allow-Origin': '*'}


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all(), 200, {'Access-Control-Allow-Origin': '*'}

    def delete(self):
        return UserModel.delete_all(), 200, {'Access-Control-Allow-Origin': '*'}


class SecretResource(Resource):
    @jwt_required()
    def get(self):
        data = [{'id': 12, 'uid': 32}]
        return jsonify(data), 200, {'Access-Control-Allow-Origin': '*'}

