from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource # 리소스 라이브러리 데이터 동작 코드
from flask import request
import mysql.connector
from mysql.connector import Error
from mysql_connection import get_connection


class MemoListResource(Resource):

    @jwt_required()
    def post(self): # 메모 추가

        data = request.get_json()
        
        user_id = get_jwt_identity() 

        try : 
            connection = get_connection()

            query = '''insert into memo
                    (title, date, content, userId)
                    values
                    (%s, %s, %s, %s);'''
            
            record = (data['title'],
                      data['date'],
                      data['content'],
                      user_id)

            cursor = connection.cursor() # 쿼리실행

            cursor.execute(query, record) 

            connection.commit() # 데이터 반영시켜라

            cursor.close()
            connection.close()            

        except Error as e:
            print(e)
            return {'result' : 'fail', 'error' : str(e) }, 500

        return {'result' : 'succes'}
    
    @jwt_required()
    def get(self) : # 내가만든메모

        user_id = get_jwt_identity()
        
        try :
            connection = get_connection()

            query = '''select *
                    from memo
                    where userId = %s
                    order by date desc;'''      

            record = ( user_id, )
            cursor = connection.cursor( dictionary=True ) # 데이터를 가져올 때
            cursor.execute( query, record )

            result_list = cursor.fetchall() # 데이터 가져옴
            
            cursor.close()
            connection.close()           

        except Error as e:
            print(e)
            return {'result': 'fail', 'error':str(e)}, 500
        
        i = 0
        for row in result_list : # result_list에서 행을 하나씩 가져온다
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            result_list[i]['date'] = row['date'].isoformat()            
            i = i + 1
 
        return {'result' : 'success', 'count':len(result_list), 'item' : result_list}
    

class MemoResource(Resource):
    
    @jwt_required()
    def put(self, memo_id): # 메모수정
        data = request.get_json()
        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''update memo
                        set title = %s, date = %s, content = %s
                        where userId = %s and id = %s;'''
            record = (data['title'],
                      data['date'],
                      data['content'],
                      user_id, memo_id)
            
            cursor = connection.cursor()
            cursor.execute( query, record )
            connection.commit()            

            cursor.close()
            connection.close()            

        except Error as e:
            print(e)
            return {'result':'fail', 'error':str(e)}, 500

        return {'result':'success'}
    
    @jwt_required()    
    def delete(self, memo_id): # 메모삭제

        user_id = get_jwt_identity()

        try : 
            connection = get_connection()
            query = '''delete from memo
                        where userId = %s and id = %s;'''
            record = (user_id, memo_id)

            cursor = connection.cursor()
            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()
            

        except Error as e:
            print(e)
            return {'result':'fail', 'error':str(e)}, 500
        
        return {'result':'success'}
    
class FollowMemoListResource(Resource) :
    
    @jwt_required()
    def get(self) : # 페이징이 포함된 친구들의 메모 가져오기

        # 1. 클라이언트로부터 데이터를 받아온다.
        # 바디에 있는 경우 request.get_json()으로 받아옴

        # query params는, 딕셔너리로 받아오고,
        # 없는 키값을 액세스 해도 에러 발생하지 않도록
        # 딕셔너리의 get 함수를 사용해서 데이터를 받아온다.

        offset = request.args.get('offset')
        limit = request.args.get('limit')
        user_id = get_jwt_identity() 

        # 딕셔너리 불러오는 함수
        # print(request.args)
        # print(request.args.get('abc')) # 없는 키값 요구해도 나옴_ 서버에서는 이걸로 처리함
        # print(request.args['abc']) # 없는 키값 요구하면 에러(400에러)_쿼리파라미터(?offset=0&limit=4)에 없다
        
        try : 
            connection = get_connection()
            query = '''select m.*, u.nickname
                    from follow f 
                    join memo m
                        on f.followeeId = m.userId
                    join user u
                        on m.userId = u.id
                    where f.followerId=%s
                    order by date desc
                    limit '''+ offset +''', '''+ limit +''';'''
            record = (user_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            print(result_list)

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result':'fail', 'error':str(e)}, 500

        i = 0
        for row in result_list : # result_list에서 행을 하나씩 가져온다
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            result_list[i]['date'] = row['date'].isoformat()            
            i = i + 1
 
        return {'result' : 'success', 'count':len(result_list), 'item' : result_list}