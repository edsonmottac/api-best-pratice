from urllib.parse import uses_netloc
from click import password_option
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from src.constants.http_status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT ## encripta passoword

import validators
# from flask_jwt_extended import jwt_required, create_refresh_token, create_access_token
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flasgger import swag_from

from src.database import User, db

auth = Blueprint("auth",__name__,url_prefix="/api/v1/auth")

@auth.post("/register")
@swag_from('./docs/auth/register.yaml')
def register():

    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

 

    if (len(password) < 6):
        return jsonify({"error":"Password is too short"},HTTP_400_BAD_REQUEST)
        

    if (not username.isalnum()  or " " in  username):
        return jsonify({'error':'Username should be alphanumeric, also no spaces'},HTTP_400_BAD_REQUEST)
        

    if not validators.email(email):
        return jsonify({'error':'Email is not valid'},HTTP_400_BAD_REQUEST)
                

    if (User.query.filter_by(email=email).first() is not None):
        return jsonify({'error':'Emais is taken '},HTTP_409_CONFLICT)
              

    if (User.query.filter_by(username=username).first() is not None):
        return jsonify({'error':'Username is taken '},HTTP_409_CONFLICT)

    pwd_hash = generate_password_hash(password)
    
    user = User(username=username, password=pwd_hash, email=email )
    db.session.add(user)
    db.session.commit() 

    return jsonify ({
        "message": "User Created",
        "User":  {
            "username":username,
            "email":email
        }
    },HTTP_200_OK)

    
@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email=request.json.get('email')
    password=request.json.get('password')

    user = User.query.filter_by(email=email).first()

    
    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh= create_refresh_token(identity=user.id)
            accesss= create_access_token(identity=user.id)

            return jsonify({
                'refresh':refresh,
                'access':accesss,
                'username':user.username,
                'email':user.email,
            },HTTP_200_OK
            )

    return jsonify({"Error": "Wrong credencials"}, HTTP_401_UNAUTHORIZED)

# Se utiliza do repfresh tocken para gerar um ourto acess token v??lido
@auth.post('/token/refresh')
@jwt_required(optional=True, refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access,
    }, HTTP_200_OK)


# requerendo o token para acessar uma rota
@auth.get("/me")
# @jwt_required()
def me():
    print(a)
    return {"user":"me"}
    