import numpy as np
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restful import Resource, reqparse, Api
from flask_jwt_extended import  jwt_required, JWTManager, create_access_token

import datetime

db = SQLAlchemy()
app = Flask(__name__)
api = Api(app)
database = 'd9mkrcud8u94f5'
host = 'ec2-54-247-72-30.eu-west-1.compute.amazonaws.com'
user = 'fqlcmcljmrgtpp'
pwd = '5a00cc2243556bdcf2159b761696cfe097b222445ffef3b39f59ee45bf79d0dc'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{user}:{pwd}@{host}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=5)

jwt = JWTManager(app)

db.init_app(app)

app.app_context().push()

db.Model.metadata.reflect(db.engine)



class Banks(db.Model):
    __table__ = db.Model.metadata.tables['MyData']
    
    ifsc = db.Column(db.String, unique=True, primary_key=True)
    bank_id = db.Column(db.Integer)
    branch = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(255), nullable=False)
    state = db.Column(db.String(255), nullable=False)
    bank_name = db.Column(db.String(255), nullable=False)
    
    def __init__(self, ifsc=None, bank_id=None, branch=None, address=None, city=None, district=None, state=None, bank_name=None):
        self.ifsc = ifsc
        self.bank_id = bank_id
        self.branch = branch
        self.address = address
        self.city = city
        self.district = district
        self.state = state
        self.bank_name = bank_name
    
    @classmethod    
    def branch_details(cls, bank, city, offset_value, limit_value):
        return cls.query.filter_by(bank_name=bank).filter_by(city=city).offset(offset_value).limit(limit_value).all()
    
    @classmethod
    def find_by_ifsc(cls, ifsc):
        return cls.query.filter_by(ifsc=ifsc).all()
    
    def json(self):
        return {'district': self.district, 'address': self.address, 'bank_id': self.bank_id, 'state': self.state, 
                'city': self.city, 'branch': self.branch, 'ifsc': self.ifsc, 'bank_name': self.bank_name}
    
        
        
class IFSC(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('ifsc', type=str, required=True, help='Ifsc of the bank')
    parser.add_argument('offset', type=int, required=False, help='Offset value')
    parser.add_argument('limit', type=int, required=False, help='Limit value')
    @jwt_required
    def get(self):
        ifsc_code = IFSC.parser.parse_args()['ifsc']
        bank_details = Banks.find_by_ifsc(ifsc_code)[0].json()
        return bank_details
    
    
class BRANCH(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('bank_name', type=str, required=True, help='Bank name')
    parser.add_argument('city', type=str, required=True, help='City name')
    parser.add_argument('offset', type=int, required=False, help='Offset value')
    parser.add_argument('limit', type = int, required=False, help='Limit value')
    @jwt_required
    def get(self):
        args = BRANCH.parser.parse_args()
        bank_name = args['bank_name']
        city = args['city']
        offset_value = args['offset']
        limit_value = args['limit']
        branch_list = list(map(lambda x: x.json(), Banks.branch_details(bank_name, city, offset_value, limit_value)))
        return {'Branch_Details': branch_list}
    

class LOGIN(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help='Username is required')
    parser.add_argument('password', type=str, required=True, help='Password is required')
    def post(self):
        args = LOGIN.parser.parse_args()
        username = args['username']
        password = args['password']
        if username != 'test' or password != 'test':
            return {"msg": "Bad username or password"}

        ret = {'access_token': create_access_token(username)}
        return ret



api.add_resource(IFSC, '/branch_ifsc')
api.add_resource(BRANCH, '/branch')
api.add_resource(LOGIN, '/login')

if __name__ == '__main__':
    app.run(debug=True)