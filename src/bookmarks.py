import json
from flask import Blueprint, jsonify, request
import validators
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required

from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from flasgger import swag_from

from src.database import Bookmark, db

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

# Cadatsrar e mostgrar em um,a só rotina
@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if (request.method == 'POST'):

        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({
                'errro':'Enter a valida value'
            }, HTTP_400_BAD_REQUEST)

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error':'URL already exists'
            }, HTTP_409_CONFLICT)

        bookmark = Bookmark(url=url,body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()


        return jsonify({
            'id':bookmark.id,
            'url':bookmark.url,
            'short_url':bookmark.short_url,
            'visits':bookmark.visits,
            'body':bookmark.body,
            'created_at':bookmark.created_at,
            'created_at':bookmark.created_at,
        }, HTTP_201_CREATED)

  
    
    else:

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 2, type=int)

        bookmarks = Bookmark.query.filter_by(
            user_id=current_user).paginate(page=page, per_page=per_page)
                

        # without paginação
        # bookmarks=Bookmark.query.filter_by(user_id=current_user)

        data=[]
        # for bkm in bookmarks: # sem paginação
        for bkm in bookmarks.items: #com paginação
            data.append({
                'id':bkm.id,
                'url':bkm.url,
                'short_url':bkm.short_url,
                'visits':bkm.visits,
                'body':bkm.body,
                'created_at':bkm.created_at,
                'created_at':bkm.created_at,
            })

        meta = {
            "page": bookmarks.page,
            'pages': bookmarks.pages,
            'total_count': bookmarks.total,
            'prev_page': bookmarks.prev_num,
            'next_page': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev,
        }
        # com isso podemos consultar assim: http://127.0.0.1:5000/api/v1/bookmarks/?page=2
        # ou assim: http://127.0.0.1:5000/api/v1/bookmarks/?page=1&per_page=11
        
        return jsonify({
            'data':data,
            'meta':meta
        },HTTP_200_OK)


@bookmarks.get("/<int:id>")    
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()


    bookmark =  Bookmark.query.filter_by(user_id = current_user,id=id).first()

    if (not bookmark):
        
        return jsonify({
            'message':'Item os not found'
        }, HTTP_404_NOT_FOUND)
    
    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'short_url':bookmark.short_url,
        'visits':bookmark.visits,
        'body':bookmark.body,
        'created_at':bookmark.created_at,
        'created_at':bookmark.created_at,
    }, HTTP_201_CREATED)


@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def editbookmarks(id):
    current_user = get_jwt_identity()
    bookmark =  Bookmark.query.filter_by(user_id = current_user,id=id).first()

    if (not bookmark):
        
        return jsonify({
            'message':'Item os not found'
        }, HTTP_404_NOT_FOUND)     

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({
            'errro':'Enter a valida value'
        }, HTTP_400_BAD_REQUEST)


    bookmark.url = url
    bookmark.body = body
    
    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK    


@bookmarks.delete("/<int:id>")    
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    
    bookmark =  Bookmark.query.filter_by(user_id = current_user,id=id).first()

    if (not bookmark):
        
        return jsonify({
            'message':'Item os not found'
        }, HTTP_404_NOT_FOUND)

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT

@bookmarks.get('/stats')
@jwt_required()
@swag_from("./docs/bookmarks/stats.yaml")
def get_stats():
    current_user = get_jwt_identity()
    data=[]

    items = Bookmark.query.filter_by(user_id = current_user).all()

    for item in items:
        new_link = {
            "visits":item.visits,
            "url":item.url,
            "id":item.id,
            "short_url":item.short_url
        }
        data.append(new_link)

    return jsonify({
        'data':data
    }, HTTP_200_OK)


