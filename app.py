from flask import Flask, jsonify, send_from_directory
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserRegister, UserLogin, User, TokenRefresh
from resources.item import Item, ItemList, UploadItemImage
from resources.store import Store, StoreList
import os

from db import db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pass12345@localhost:5432/flask-inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

migrate = Migrate(app, db)
api = Api(app)

# 1 - flask db init
# 2 - flask db migrate
# 3 - flask db upgrade

@app.route("/")
def home():
    return render_template('index.html')


"""
JWT related configuration. The following functions includes:
1) add claims to each jwt
2) customize the token expired error message 
"""
app.config['JWT_SECRET_KEY'] = 'jose'  # we can also use app.secret like before, Flask-JWT-Extended can recognize both
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'media')
app.config['JWT_BLACKLIST_ENABLED'] = True  # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  # allow blacklisting for access and refresh tokens
jwt = JWTManager(app)

"""
`claims` are data we choose to attach to each jwt payload
and for each jwt protected endpoint, we can retrieve these claims via `get_jwt_claims()`
one possible use case for claims are access level control, which is shown below
"""
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:   # instead of hard-coding, we should read from a config file to get a list of admins instead
        return {'is_admin': True}
    return {'is_admin': False}


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):  # we have to keep the argument here, since it's passed in by the caller internally
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401

# JWT configuration ends
api.add_resource(Store, "/store/<string:name>")
api.add_resource(StoreList, "/stores")
api.add_resource(Item, "/item/<string:name>")
api.add_resource(ItemList, "/items")
api.add_resource(UploadItemImage, "/items/image")
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(TokenRefresh, '/refresh')

# Media files
@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
    )

from models.user import UserModel
from models.store import StoreModel
from models.item import ItemModel

db.init_app(app)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
