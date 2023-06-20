from flask import Flask 
from flask_restful import Api
from config import Config
from resources.user import UserRegisterResource, UserLoginResource, UserLogoutResource, jwt_blocklist
from resources.memo import MemoListResource, MemoResource, FollowMemoListResource
from resources.follow import FollowResource
from flask_jwt_extended import JWTManager



app = Flask(__name__)

print('app 변수 생성') # 디버깅 

app.config.from_object(Config)

jwt = JWTManager(app)

print('jwt 매니저 초기화') # 디버깅

@jwt.token_in_blocklist_loader # 유효하지 않은 블락리스트에 있는 토큰 관리하겠다
def check_if_token_is_revoked( jwt_header, jwt_payload ) :
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

api = Api(app)

api.add_resource( UserRegisterResource , '/user/register') # 회원가입
api.add_resource( UserLoginResource , '/user/login') # 로그인
api.add_resource( UserLogoutResource, '/user/logout' ) # 로그아웃
api.add_resource( MemoListResource, '/memo' ) # 내가만든메모, 메모생성
api.add_resource( MemoResource, '/memo/<int:memo_id>' ) # 메모 수정삭제
api.add_resource( FollowResource, '/follow/<int:followee_id>') # 친구 맺기, 친구 끊기
api.add_resource( FollowMemoListResource, '/follow/memo' )

if __name__ == '__main__' : 
    app.run()