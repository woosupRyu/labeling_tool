# -*- coding: utf-8 -*-
from . import querys
from .utils.img_util import save_img
from .utils.util import save_json, find_id_name
from os.path import join

import pymysql
import inspect


class DB:
    """
    MySQL server와 정보를 주고받는 class 입니다.
    """
    def __init__(self, ip, port, user, password, db_name, charset='utf8mb4'):
        """
        DB class를 초기화하는 함수

        pymysql.connect()를 이용해 MySQL과 연결

        mysql 서버의 변수 설정
            wait_timeout: 활동하지 않는 커넥션을 끊을때까지 서버가 대기하는 시간
            interactive_timeout: 활동중인 커넥션이 닫히기 전까지 서버가 대기하는 시간
            max_connections: 한번에 mysql 서버에 접속할 수 있는 클라이언트 수

        Args:
            ip (str): MySQL 서버에 로그인하기위한 ip 주소
            port (int): 포트 포워딩을 위한 포트
            user (str): MySQL 서버에 로그인을 위한 아이디
            password (str): MySQL 서버에 로그인을 위한 비밀번호
            db_name (str): 데이터베이스 네임
            charset (str): 문자 인코딩 방식

        Examples:

        .. code-block:: python

            mydb = DB(ip='192.168.10.69',
                      port=3306,
                      user='root',
                      password='return123',
                      db_name='test')
        """
        try:
            self.db = pymysql.connect(host=ip, port=port, user=user, passwd=password, charset=charset)
            print("setting on")

            with self.db.cursor() as cursor:
                query = 'SET GLOBAL wait_timeout=31536000'
                cursor.execute(query)

                query = 'SET GLOBAL interactive_timeout=31536000'
                cursor.execute(query)

                query = 'SET GLOBAL max_connections=100000'
                cursor.execute(query)

                query = 'SET GLOBAL max_user_connections=100000'
                cursor.execute(query)

                query = 'SET GLOBAL max_error_count=65535'
                cursor.execute(query)

                query = 'SET GLOBAL max_connect_errors=4294967295'
                cursor.execute(query)

                query = "SET @@autocommit=0"
                cursor.execute(query)

                query = "CREATE DATABASE {}".format(db_name)
                cursor.execute(query)
        except Exception as e:
            print('already init DB')
            print(e)
        else:
            self.db.commit()
        finally:
            self.db.select_db(db_name)

    # ------------------------------------------기본 쿼리------------------------------------------

    def init_table(self) -> bool:
        """
        table을 생성합니다.

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                for i, sql in enumerate(querys.initial_queries):
                    print('{} 번째 sql 실행중...'.format(i + 1))
                    cursor.execute(sql)

                cursor.execute("SHOW TABLES")
                for line in cursor.fetchall():
                    print(line)
        except Exception as e:
            print('table is already exist')
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def init_table_no_print(self) -> bool:
        """
        table을 생성합니다. print 없

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                for i, sql in enumerate(querys.initial_queries):
                    cursor.execute(sql)
                cursor.execute("SHOW TABLES")
        except Exception as e:
            print('table is already exist')
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def del_table(self, table) -> bool:
        """
        mysql databse에 있는 table의 모든 row를 지웁니다.(테이블은 유지)

        Args:
            table (str): 지우고자하는 table

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "DELETE FROM {}".format(table)
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def drop_table(self, table) -> bool:
        """
        mysql databse에 있는 table을 지웁니다.(테이블 자체를 없애버림)

        Args:
            table (str): 지우고자하는 table

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "DROP TABLE " + table
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_environment(self, env_id, broker_ip, floor, width, height, depth) -> bool:
        """
        Environment table에 row 추가

        Args:
            env_id (str): 냉장고의 device id
            broker_ip (str): 냉장고와 연결된 broker ip
            floor (str) : 냉장고 층
            width (str): 냉장고 층 가로길이
            height (str): 냉장고 층 세로길이
            depth (str): 냉장고 층 높이

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Environment(env_id, broker_ip, floor, width, height, depth) ' \
                        'VALUES(%s, %s, %s, %s, %s, %s)'
                values = (env_id, broker_ip, floor, width, height, depth)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_environment(self, env_id, broker_ip=None,
                           floor=None, width=None, height=None, depth=None) -> bool:
        """
        Environment table의 row 값 갱신

        Args:
            env_id (str): Enviroment table의 env_id
            floor (str): 냉 장고 층
            width (str): 냉장고 층 가로 길이
            height (str): 냉장고 층 세로 길이
            depth (str): 냉장고 층 높이

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Environment SET '
                query_tail = ' WHERE env_id={}'.format(env_id)
                if broker_ip is not None:
                    query_head += "broker_ip='{}', ".format(broker_ip)
                if floor is not None:
                    query_head += 'floor={}, '.format(floor)
                if width is not None:
                    query_head += 'width={}, '.format(width)
                if height is not None:
                    query_head += 'height={}, '.format(height)
                if depth is not None:
                    query_head += 'depth={}, '.format(depth)
                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_grid(self, width, height) -> bool:
        """
        Grid table row 추가

        Args:
            width (str): grid 가로 칸 개수
            height (str): grid 세로 칸 개수

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Grid(width, height) ' \
                        'VALUES(%s, %s)'
                values = (width, height)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_grid(self, grid_id, width=None, height=None) -> bool:
        """
        Grid table의 특정 id row 값 갱신

        Args:
            grid_id (str): Grid table의 (grid_id)
            width (str): grid 가로 칸 수
            height (str): grid 세로 칸 수

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Grid SET '
                query_tail = ' WHERE grid_id={}'.format(grid_id)
                if width is not None:
                    query_head += 'width={}, '.format(width)
                if height is not None:
                    query_head += 'height={}, '.format(height)
                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_supercategory(self, super_name) -> bool:
        """
        SuperCategory table에 row 추가

        Arg:
            super_name (str): 상위 카테고리 물체 이름 ex) 생수

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO SuperCategory(super_name) ' \
                        'VALUES(%s)'
                values = (super_name)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_supercategory(self, super_id, super_name=None) -> bool:
        """
        SuperCategory table의 특정 id의 row 값 갱신

        Args:
            super_id (str): SuperCategory table의 id
            super_name (str): 물체의 이름 ex) 삼다수

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE SuperCategory SET '
                query_tail = ' WHERE super_id={}'.format(super_id)
                if super_name is not None:
                    query_head += "super_name='{}', ".format(super_name)
                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_image(self, env_id, img, type, check_num) -> bool:
        """
        Image table에 row 추가

        Args:
            env_id (str): Environment table의 (env_id)
            img (Image): image data
            type (str): 합성된 이미지인지 아닌지 -> 1: original, 2: mix, 3: synthesize

            check_num (str): 검수표시할 check 컬럼

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Image(env_id, img, type, check_num) ' \
                        'VALUES(%s, _binary%s, %s, %s)'
                values = (env_id, img, type, check_num)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_image(self, img_id, env_id=None, img=None, type=None, check_num=None) -> bool:
        """
        Image table의 (id)의 row 값 갱신

        Args:
            img_id (str): Image table의 특정 id(primary key)
            env_id (str): Image table의 env_id(foreigner key)
            img (image): image 정보
            type (str): 합성된 이미지 인지 아닌지 -> 1: original, 2: mix, 3: synthesize
            check_num (str): 검수표시할 check 컬럼

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Image SET '
                query_tail = ' WHERE img_id={}'.format(img_id)
                if env_id is not None:
                    query_head += 'env_id={}, '.format(env_id)
                if img is not None:
                    query_head += "img=x'{}' , ".format(img.hex())
                if type is not None:
                    query_head += 'type={}, '.format(type)
                if check_num is not None:
                    check_num += 'check_num={}, '.format(check_num)
                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_location(self, grid_id, x, y) -> bool:
        """
        Location table에 row 추가

        Args:
            grid_id (str): Grid table의 (id)
            x (str): 물체의 가로 좌표
            y (str): 물체의 세로 좌표

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Location(grid_id, x, y) ' \
                        'VALUES(%s, %s, %s)'
                values = (grid_id, x, y)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_location(self, loc_id, grid_id=None, x=None, y=None) -> bool:
        """
        Location table의 특정 id 값 갱신

        Args:
            loc_id (str): Location table의 특정 id(primary key)
            grid_id (str): Grid table의 특정 id(foreigner key)
            x (str): 물체의 x 좌표
            y (str): 물체의 y 좌표

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Location SET '
                query_tail = ' WHERE loc_id={}'.format(loc_id)
                if grid_id is not None:
                    query_head += 'grid_id={}, '.format(grid_id)
                if x is not None:
                    query_head += 'x={}, '.format(x)
                if y is not None:
                    query_head += 'y={}, '.format(y)
                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_category(self, super_id, cat_name, width, height, depth, iteration, thumbnail) -> bool:
        """
        Category table에 row 추가

        Args:
            super_id (str): SuperCategory table의 특정 id(foreigner key)
            cat_name (str): 물품의 이름
            width (str): 물체의 가로 크기
            height (str): 물체의 세로 크기
            depth (str): 물체의 높이
            iteration (str): 물체 촬영 횟수
            thumbnail (image): 썸네일 이미지

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Category(super_id, cat_name, width, height, depth, iteration, thumbnail) ' \
                        'VALUES(%s, %s, %s, %s, %s, %s, %s)'
                values = (super_id, cat_name, width, height, depth, iteration, thumbnail)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_category(self, cat_id, super_id=None, cat_name=None, width=None,
                        height=None, depth=None, iteration=None, thumbnail=None) -> bool:
        """
        Category table의 특정 id의 row 정보 갱신

        Args:
            cat_id (str): Category table의 특정 id(primary key)
            super_id (str): superCategory의 id(foreigner key)
            cat_name (str): 물품의 이름
            width (str): 물체의 가로 크기
            height (str): 물체의 세로 크기
            depth (str): 물체의 높이
            iteration (str): 물체 촬영 횟수
            thumbnail (image): 썸네일 이미지

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Category SET '
                query_tail = ' WHERE cat_id={}'.format(cat_id)
                if super_id is not None:
                    query_head += 'super_id={}, '.format(super_id)
                if cat_name is not None:
                    query_head += "cat_name='{}', ".format(cat_name)
                if width is not None:
                    query_head += 'width={}, '.format(width)
                if height is not None:
                    query_head += 'height={}, '.format(height)
                if depth is not None:
                    query_head += 'depth={}, '.format(depth)
                if iteration is not None:
                    query_head += 'iteration={}, '.format(iteration)
                if thumbnail is not None:
                    query_head += "thumbnail=x'{}' , ".format(thumbnail.hex())
                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_object(self, img_id, loc_id, cat_id, iteration, mix_num, aug_num='-1') -> bool:
        """
        Object table에 row 추가

        Args:
            img_id (str or None): Image table의 id(foreigner key)
            loc_id (str): Location table의 id(foreigner key)
            cat_id (str or None): Category table의 id(foreigner key)
            iteration (str): 물체를 방향 별로 찍어야하는 횟수
            mix_num (str): mix 이미지에 대한 정보
            aug_num (str): augumentation img에 대한 정보, -1일땐 합성된 이미지가 아님

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Object(loc_id, cat_id, img_id, iteration, mix_num, aug_num) ' \
                        'VALUES(%s, %s, %s, %s, %s, %s)'
                values = (loc_id, cat_id, img_id, iteration, mix_num, aug_num)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_object(self, obj_id, img_id=None, loc_id=None, cat_id=None,
                      iteration=None, mix_num=None, aug_num=None) -> bool:
        """
        Object table의 특정 id 정보 갱신

        Args:
            obj_id (str): Object table의 특정 obj_id(primary key)
            img_id (str or None): Image talbe의 특정 id(foreigner key)
            loc_id (str): Location table의 특정 id(foreigner key)
            cat_id (str): Category table의 특정 id(foreigner key)
            iteration (str): 물체를 방향 별로 찍어야하는 횟수
            mix_num (str): mix 이미지에 대한 정보
            aug_num (str): augumentation img에 대한 정보

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Object SET '
                query_tail = ' WHERE obj_id={}'.format(obj_id)
                if img_id is not None:
                    query_head += 'img_id={}, '.format(img_id)
                if loc_id is not None:
                    query_head += 'loc_id={}, '.format(loc_id)
                if cat_id is not None:
                    query_head += 'cat_id={}, '.format(cat_id)
                if iteration is not None:
                    query_head += 'iteration={}, '.format(iteration)
                if mix_num is not None:
                    query_head += 'mix_num={}, '.format(mix_num)
                if aug_num is not None:
                    query_head += 'aug_num={}, '.format(aug_num)

                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_bbox(self, obj_id, x, y, width, height) -> bool:
        """
        Bbox table에 row 추가

        Args:
            obj_id (str): Object table의 obj_id(foreigner key)
            x (str): Bbox의 왼쪽 시작 점 x 좌표
            y (str): Bbox의 왼쪽 시작 점 y 좌표
            width (str): Bbox의 가로 크기
            height (str): Bbox의 세로 크기

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Bbox(obj_id, x, y, width, height) ' \
                        'VALUES(%s, %s, %s, %s, %s)'
                values = (obj_id, x, y, width, height)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_bbox(self, bbox_id, obj_id=None, x=None, y=None, width=None, height=None) -> bool:
        """
        Bbox table의 특정 id 정보 갱신

        Args:
            bbox_id (str): Bbox table의 특정 bbox_id(primary key)
            obj_id (str): Object table의 특정 obj_id
            x (str): Bbox의 왼쪽 시작점 x 좌표
            y (str): Bbox의 왼쪽 시작점 y 좌표
            width (str): Bbox의 가로 크기
            height (str): Bboxm의 세로 크기

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Bbox SET '
                query_tail = ' WHERE bbox_id={}'.format(bbox_id)
                if obj_id is not None:
                    query_head += 'obj_id={}, '.format(obj_id)
                if x is not None:
                    query_head += 'x={}, '.format(x)
                if y is not None:
                    query_head += 'y={}, '.format(y)
                if width is not None:
                    query_head += 'width={}, '.format(width)
                if height is not None:
                    query_head += 'height={}, '.format(height)
                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_mask(self, obj_id, x, y) -> bool:
        """
        Mask table의 id row 추가

        Args:
            obj_id (str): Object table의 obj_id(foreigner key)
            x: Mask 점의 x 좌표
            y: Mask 점의 y 좌표

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'INSERT INTO Mask(obj_id, x, y) ' \
                        'VALUES(%s, %s, %s)'
                values = (obj_id, x, y)
                cursor.execute(query, values)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_mask(self, mask_id, obj_id=None, x=None, y=None) -> bool:
        """
        Mask table의 특정 id의 row 갱신

        Args:
            mask_id: Mask table의 id(primary key)
            obj_id (str): Object table의 id(foreigner key)
            x: Mask 점의 x 좌표
            y: Mask 점의 y 좌표

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'UPDATE Mask SET '
                query_tail = ' WHERE mask_id={}'.format(mask_id)
                if obj_id is not None:
                    query_head += 'obj_id={}, '.format(obj_id)
                if x is not None:
                    query_head += 'x={}, '.format(x)
                if y is not None:
                    query_head += 'y={}, '.format(y)

                query = query_head[:-2]
                query += query_tail
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def list_table(self, table):
        """
        mysql databse에 있는 특정 table의 모든 값을 가져옵니다.

        Args:
            table (str): 조회하기 원하는 table 이름

        Return:
            tuple ()(): 특정 table의 모든 값

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = 'SELECT * FROM ' + table
                cursor.execute(query)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3], '_', table)
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def delete_table(self, id, table) -> bool:
        """
        특정 table의 특정 Primary Key id의 row를 가져옵니다.

        Args:
            id (str): 특정 table의 primary key (id)
            table (str): table 이름

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                id_name = find_id_name(table)
                query = "DELETE FROM {0} WHERE {1}={2}".format(table, id_name, id)
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print('Table name:', table)
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def get_table(self, id, table):
        """
        특정 table의 특정 Primary Key id의 row를 가져옵니다.

        Args:
            id (str): 특정 table의 primary key (id)
            table (str): 조회하기 원하는 table 이름

        Return:
            tuple(): 해당 id의 row 값

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                id_name = find_id_name(table)
                query = "SELECT * From {0} WHERE {1}={2}".format(table, id_name, id)
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print('Table name:', table)
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_last_id(self, table):
        """
        table의 마지막 (id) 조회

        Args:
            table (str): table 이름

        Return:
            int: 마지막 id 값

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                id_name = find_id_name(table)
                query = "SELECT MAX({0}) FROM {1}".format(id_name, table)
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print('Table name:', table)
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v[0]:
                return v[0]
            else:
                return None

# ------------------------------------------복잡한 쿼리------------------------------------------

    def get_grid_id(self, grid_w_h):
        """
        Grid table의 (grid_id) 반환

        Args:
            grid_w_h (str): Grid table의 (width), (height)

        Return:
            int: Grid table의 (grid_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            w, h = grid_w_h.split('x')
            with self.db.cursor() as cursor:
                query = "SELECT grid_id FROM Grid WHERE width=%s AND height=%s"
                value = (w, h)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return None
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_super_id_SN(self, super_name):
        """
        SuperCategory table의 (super_id) 반환

        Args:
            super_name (str): SuperCategory table의 (super_name)

        Return:
            int: SuperCategory table의 (super_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT super_id FROM SuperCategory WHERE super_name='{}'".format(super_name)
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_super_id_CI(self, cat_id):
        """
        Category table의 (cat_id)를 받아
        Category table의 (super_id)를 반환

        Args:
            cat_id (str): Category table의 (cat_id)

        Return:
            int: (super_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT super_id FROM Category WHERE cat_id=%s"
                value = (cat_id)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_super_name(self, super_id):
        """
        SuperCategory table의 (super_id)를 받아
        SuperCategory table의 (super_name)을 반환함

        Args:
            super_id (str): SuperCategory table의 (super_id)

        Return:
            int: SuperCategory table의 (super_name)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT super_name FROM SuperCategory WHERE super_id=%s"
                value = (super_id)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_loc_id(self, grid_id, loc_x_y):
        """
        Location table의 (loc_id) 반환

        Args:
            grid_id (str): Location table의 (grid_id)
            loc_x_y (str): Location table의 (x), (y)

        Return:
            int: Location table의 (loc_id)

            None: 값 없음

            False: 쿼리 실패
        """
        x, y = loc_x_y.split('x')
        try:
            with self.db.cursor() as cursor:
                query = "SELECT loc_id FROM Location WHERE grid_id=%s AND x=%s AND y=%s"
                value = (grid_id, x, y)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_loc_id_GL(self, grid_w_h, loc_x_y):
        """
        Grid table의 (width, height)와 Location table의 (x, y)를 입력받아
        Location table의 (loc_id) 반환하는 함수

        Args:
            grid_w_h (str): Grid table의 (width), (height) 정보
            loc_x_y (str): Location table의 (x), (y) 정보

        Return:
            int: Location table의 (loc_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            w, h = grid_w_h.split('x')
            x, y = loc_x_y.split('x')
            with self.db.cursor() as cursor:
                query = "SELECT loc_id FROM Location WHERE x=%s AND y=%s " \
                        "AND grid_id=(SELECT grid_id FROM Grid WHERE width=%s AND height=%s)"
                value = (x, y, w, h)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_loc(self, grid_id):
        """
        Location table의 (grid_id)를 입력 받아
        Location table의 row 반환

        Args:
            grid_id (str): Location table의 (grid_id)

        Return:
            tuple()(): Location table의 (loc_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT * FROM Location WHERE grid_id=%s"
                value = (grid_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_cat_id_SI(self, super_id, cat_name):
        """
        Category table의 (cat_id) 반환

        Args:
            super_id (str): Category table의 (super_id)
            cat_name (str): Category table의 (cat_name)

        Return:
            int: Category table의 (cat_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT cat_id FROM Category WHERE super_id={0} AND cat_name='{1}'".format(super_id, cat_name)
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_cat_id_SN(self, super_name, cat_name):
        """
        SuperCateogry table의 (super_name)과 Category table의 (cat_name)을 받아
        Category table의 (cat_id) 반환

        Args:
            super_name (str): SuperCategory table의 (super_name)
            cat_name (str): Category table의 (cat_name)

        Return:
            int: Category table의 (cat_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT cat_id FROM Category WHERE cat_name=%s AND " \
                        "super_id=(SELECT super_id FROM SuperCategory WHERE super_name='{0}')".format(super_name)
                value = (cat_name)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_img_id(self, obj_id):
        """
        Object table의 (img_id) 반환

        Args:
            obj_id (str): 조회하기 원하는 Object table의 (obj_id)

        Return:
            int: 해당하는 Object table의 (img_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT img_id FROM Object WHERE obj_id=%s"
                value = (obj_id)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_cat_id_obj(self, obj_id):
        """
        Object table의 (obj_id)를 받아 (cat_id)를 얻음

        Args:
            obj_id (str): Object table의 (obj_id)

        Return:
            int: Object table의 (cat_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT cat_id FROM Object WHERE obj_id=%s"
                value = obj_id
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_obj_id_img(self, img_id):
        """
        Object table의 (img_id)를 받아 (obj_id)들을 얻음

        Args:
            img_id (str): Object table의 (img_id)

        Return:
            tuple (): Object table의 (obj_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT obj_id FROM Object WHERE img_id=%s"
                value = (img_id)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_obj_id(self, cat_id):
        """
        Object table의 (cat_id)를 입력 받아 (cat_id)와 (mix_num)=-1인
        Object table의 (obj id)들 반환

        Args:
            cat_id (str): Object table의 (cat_id)

        Return:
            tuple () : Object_table의 (obj_id) row

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT obj_id FROM Object " \
                        "WHERE cat_id=%s AND mix_num=-1"
                value = (cat_id)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_max_mix_num(self):
        """
        Location table의 (x)=0, (y)=0인 mix row 찾음 => (loc_id)
        찾은 (loc_id)를 통해
        Object table의 mix_num 중 가장 큰 값을 반환

        Return:
            int: Object table의 (mix_num) 중 가장 큰 값

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT MAX(Object.mix_num) " \
                        "FROM(SELECT loc_id FROM Location WHERE x=0 AND y=0) AS Loc " \
                        "INNER JOIN Object ON Object.loc_id=Loc.loc_id"
                cursor.execute(query)
                mix_num = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if mix_num:
                return mix_num[0]
            else:
                return None

    def get_bbox_id(self, obj_id):
        """
        Object table의 (obj_id)를 받아
        Bbox table의 (bbox_id) 반환

        Args:
            obj_id (str): Object table의 (obj_id)

        Return:
            tuple (): Bbox table의 (bbox_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT bbox_id FROM Bbox WHERE obj_id=%s"
                value = (obj_id)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_bbox(self, obj_id):
        """
        Object table의 (obj_id)를 가지는
        Bbox table의 (x), (y), (width), (height) 2차원 리스트로 반환

        Args:
            obj_id (str): 조회하기 원하는 Bbox table의 (obj_id)

        Return:
            tuple ()(): Bbox table의 ((x, y, width, height), (...))

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT x, y, width, height from Bbox WHERE obj_id=%s"
                value = (obj_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_bbox_img(self, img_id):
        """
        Object table의 (img_id)를 받아 (obj_id)들을 가져옴
        얻은 (obj_id)들로 Bbox table의 row 조회

        Args:
            img_id (str): Object table의 (img_id)

        Return:
            tuple ()(): Bbox table의 row

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT * FROM Bbox " \
                        "WHERE obj_id IN (SELECT obj_id FROM Object WHERE img_id=%s)"
                value = (img_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_mask_id(self, obj_id):
        """
        Object table의 (obj_id)를 받아
        Mask table의 (mask_id) 반환

        Args:
            obj_id (str): Object table의 (obj_id)

        Return:
            tuple (): Mask table의 (mask_id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT mask_id FROM Mask WHERE obj_id=%s"
                value = (obj_id)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_obj_max_iter(self):
        """
        Object table의 (iteration) 중 가장 높은 값 반환

        Return:
            int: Object table의 iteration

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT MAX(iteration) FROM Object"
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_bbox_img_id(self, img_id):
        """
        Object table의 (img_id)를 입력 받아 Object table의 (obj_id) 찾음.
        찾은 (obj_id)로
        Bbox table의 (x), (y), (width), (height)와
        Object_table의 (cat_id), (loc_id) 반환

        Args:
            img_id (str) : Object table의 (img_id)

        Return:
            tuple ()(): ((cat_id, loc_id, x, y, width, height), (...)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT O.cat_id, O.loc_id, Bbox.x, Bbox.y, Bbox.width, Bbox.height " \
                        "FROM (SELECT obj_id, cat_id, loc_id FROM Object WHERE img_id=%s) AS O " \
                        "INNER JOIN Bbox ON O.obj_id=Bbox.obj_id"
                value = (img_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_obj_max_aug(self):
        """
        Object table의 (aug_num) 중 max값 반환

        Return:
            int: Object table의 aug_num

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT MAX(aug_num) FROM Object"
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_obj_id_args(self, loc_id, cat_id, iteration, mix_num, aug_num):
        """
        Object table의 (obj_id) 반환

        Args:
            loc_id (str): Object table의 (loc_id)
            cat_id (str): Object table의 (cat_id)
            iteration (str): Object table의 (iteration)
            mix_num (str): Object table의 (mix_num)
            aug_num (str): Object table의 (aug_num)

        Return:
            int: Object table의 (obj_id)

            None: 값 없음

            False: 조회 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT obj_id FROM Object " \
                        "WHERE loc_id=%s AND cat_id=%s AND iteration=%s AND mix_num=%s AND aug_num=%s"
                value = (loc_id, cat_id, iteration, mix_num, aug_num)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_mask_obj_id(self, obj_id):
        """
        Mask Table의 (obj_id)를 가지는 Mask table의 (id), (x), (y)를
        2차원 튜플로 반환

        Args:
            obj_id (str): 조회하기 원하는 Mask table의 (obj_id)

        Return:
            tuple ()(): ((mask_id, x, y), (...))

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT mask_id, x, y from Mask WHERE obj_id=%s"
                value = (obj_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_max_G_size(self):
        """
        Grid table의 (width), (height) 값의 최댓값 반환

        Return:
            tuple: (MAX(width), MAX(height))

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT MAX(width), MAX(height) FROM Grid"
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_obj_id_cat_id_NULL(self, loc_id, iteration, mix_num, aug_num):
        """
        Object table의 (loc_id), (iteration), (mix_num), (aug_num)를 입력받고 (cat_id)가 NULL에
        해당하는 Object table의 (obj_id)를 반환
        단, 해당하는 Object table의 row가 여러개 존재할 경우
        MAX(obj_id) 반환

        Args:
            loc_id (str) : Object table의 (loc_id)
            iteration (str) : Object table의 (iteration)
            mix_num (str) : Object table의 (mix_num)
            aug_num (str) : Object table의 (aug_num)

        Return:
            int: Object table의 (obj_id)

            None: 조회 실패

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT MAX(obj_id) FROM Object " \
                        "WHERE loc_id=%s AND cat_id IS NULL AND iteration=%s AND mix_num=%s AND aug_num=%s"
                value = (loc_id, iteration, mix_num, aug_num)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def get_img_id_type(self, type):
        """
        Image table의 (type)이 type인
        Image table의 (img_id) 반환

        Args:
            type (str): Image table의 (type) -> 1: original, 2: mix, 3: synthesize

        Return:
            tuple () : Image table의 (img_id)
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT img_id FROM Image WHERE type=%s"
                value = (type)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def list_bbox(self, obj_id):
        """
        Bbox table의 (obj_id)를 이용해
        Bbox table의 row 반환

        Args:
            obj_id (str): Bbox table의 (obj_id)

        Return:
            tuple()(): Bbox table의 row

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT * FROM Bbox WHERE obj_id=%s"
                value = (obj_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def list_obj(self, cat_id, loc_ids):
        """
        Object table의 (cat_id), (loc_ids)를 입력 받아
        Object table의 row들을 반환하는 함수

        Args:
            cat_id (str): Object table의 (cat_id)
            loc_ids (tuple): Object table의 (loc_id)들

        Return:
            tuple()(): Object table의 row

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query_head = 'SELECT * FROM Object WHERE (cat_id=' + cat_id + ') AND ('
                for loc_id in loc_ids:
                    query_head += 'loc_id={} OR '.format(loc_id[0])

                query = query_head[:-4] + ')'
                cursor.execute(query)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def list_img_id_TC(self, type, check_num):
        """
        Image table의 (type, check_num)인
        Image table의 (id)를 반환

        Args:
            type(str): Image table의 (type) -> 1: original, 2: mix, 3: synthesize
            check_num(str): Image table의 (check_num) -> (0 : 완료, 1 : 미진행, 2 : 거절)

        Return:
            tuple (): Image table의 (id)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT img_id FROM Image WHERE type=%s AND check_num=%s"
                value = (type, check_num)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def list_obj_CN(self, grid_id, cat_id, check_num):
        """
        Object table의 (cat_id)가 NULL이고, Location table의 (grid_id) 일때,
        Image table의 (check_num)이 check_num과 같으면
        Object table의 row를 반환하는 함수
        Args:
            grid_id (str): Location table의 (grid_id)
            cat_id (str): Object table의 (cat_id)
            check_num(str): Image table의 (check_num) 값과 비교될 값 -> (0 : 완료, 1 : 미진행, 2 : 거절)
        Return:
            tuple ()(): Object table의 (row)s
            None: 값 없음
            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT * FROM Object WHERE obj_id IN (SELECT C.obj_id " \
                        "   FROM (SELECT tmp.obj_id, Image.check_num " \
                        "       FROM (SELECT Obj.obj_id, Obj.img_id " \
                        "           FROM (SELECT obj_id, img_id, loc_id " \
                        "               FROM Object WHERE cat_id=%s) AS Obj " \
                        "           INNER JOIN (SELECT loc_id FROM Location WHERE grid_id=%s) AS Loc " \
                        "           ON Loc.loc_id=Obj.loc_id) AS tmp " \
                        "       INNER JOIN Image ON Image.img_id=tmp.img_id) AS C " \
                        "WHERE check_num=%s)"
                value = (cat_id, grid_id, check_num)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def list_obj_CN_NULL(self, grid_id, check_num):
        """
        Object table의 (cat_id)가 NULL이고, Location table의 (grid_id) 일때,
        Image table의 (check_num)이 check_num과 같은 것 중에
        MAX(obj_id)인 Object table의 row를 반환하는 함수

        Args:
            grid_id(str): Location table의 (grid_id)
            check_num(str): Image table의 (check_num) 값과 비교될 값 -> (0 : 완료, 1 : 미진행, 2 : 거절)

        Return:
            tuple (): Object table의 (row)

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT * FROM Object " \
                        "WHERE obj_id IN (SELECT C.obj_id " \
                        "   FROM (SELECT tmp.obj_id, Image.check_num " \
                        "       FROM (SELECT Obj.obj_id, Obj.img_id " \
                        "           FROM (SELECT obj_id, img_id, loc_id " \
                        "               FROM Object WHERE cat_id IS NULL) AS Obj " \
                        "           INNER JOIN (SELECT loc_id FROM Location WHERE grid_id=%s) AS Loc " \
                        "           ON Loc.loc_id=Obj.loc_id) AS tmp " \
                        "       INNER JOIN Image ON Image.img_id=tmp.img_id) AS C " \
                        "WHERE check_num=%s) " \
                        "ORDER BY obj_id DESC "
                value = (grid_id, check_num)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def check_img_CN(self, img_id) -> bool:
        """
        Image table의 이미지의 check_num을 반환

        Args:
            img_id (str): 조회하기 원하는 Object table의 id

        Return:
            int (0, 1, 2): 해당 object의 이미지 검수여부 반환

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = 'SELECT check_num FROM Image WHERE id=' + img_id
                cursor.execute(query)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v[0]
            else:
                return None

    def check_obj_id(self, loc_id, cat_id, iteration, mix_num) -> bool:
        """
        Object table의 (loc_id, category_id, iteration)를 입력 받아
        Object table의 특정 (id)를 check 하는 함수

        Args:
            loc_id (str): Object table의 loc_id
            cat_id (str): Object table의 category_id
            cat_id (str): Object table의 iteration
            mix_num (str): Object table의 mix_num

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT obj_id FROM Object " \
                        "WHERE loc_id=%s AND cat_id=%s AND iteration=%s AND mix_num=%s"
                value = (loc_id, cat_id, iteration, mix_num)
                cursor.execute(query, value)
                obj_id = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if obj_id:
                return True
            else:
                return False

    def check_nomix_OBM(self, cat_id) -> bool:
        """
        Object table의 (cat_id)가 입력받은 값을 가지고 (mix_num)이 -1인 Object table의 row가 존재하고
        해당하는 모든 Object table의 row에 대한 Bbox table의 row와 Mask table의 row가 둘다 존재할 경우 True 반환
        이외의 경우 False 반환

        Args:
            cat_id (str): Object table의 (cat_id)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                # Mask query
                query = "SELECT mask_id FROM Mask " \
                        "WHERE obj_id IN (SELECT obj_id FROM Object WHERE cat_id=%s AND mix_num=-1)"
                value = (cat_id)
                cursor.execute(query, value)
                mask_ids = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if mask_ids:
                return True
            else:
                return False

    def check_cat_id(self, super_name, cat_name) -> bool:
        """
        SuperCateogry table의 (super_name)과 Category table의 (cat_name)을 입력받아
        Category table의 특정 (cat_id)가 존재하는지 check하는 함수

        Args:
            super_name (str): SuperCategory table의 (super_name)
            cat_name (str): Category table의 (cat_name)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT cat_id FROM Category WHERE cat_name=%s AND " \
                        "super_id IN (SELECT super_id FROM SuperCategory WHERE super_name=%s)"
                value = (super_name, cat_name)
                cursor.execute(query, value)
                v = sum(cursor.fetchall(), ())
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return True
            else:
                return False

    def update_img_CN_OI(self, obj_id, check_num) -> bool:
        """
        Object table의 (obj_id)를 입력 받아
        Image table의 (check_num)을 update 하는 함수

        Args:
            obj_id (str): Object table의 (obj_id)
            check_num (str): Image table의 (check_num)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "UPDATE Image SET check_num=%s " \
                        "WHERE img_id=(SELECT img_id FROM Object WHERE obj_id=%s)"
                value = (check_num, obj_id)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_img_CN_II(self, img_id, check_num) -> bool:
        """
        Image table의 (check_num) update

        Args:
            img_id (str): Object table의 (obj_id)
            check_num (str): Image table의 (check_num)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "UPDATE Image SET check_num=%s WHERE img_id=%s"
                value = (check_num, img_id)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_mix_obj_img(self, iteration, img_id) -> bool:
        """
        Object table의 (cat_id)가 NULL이고 (iteration)이 iteration인
        Object table row를 (img_id)를 img_id로 업데이트

        Args:
            iteration(str) : Object table의 (iteration)
            img_id(str) : Object table의 (img_id)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "UPDATE Object SET img_id=%s " \
                        "WHERE cat_id IS NULL AND iteration=%s"
                value = (img_id, iteration)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_img_img_OI(self, obj_id, img) -> bool:
        """
        Object table의 (obj_id)를 입력 받아
        Image table의 (img) update 하는 함수

        Args:
            obj_id (str): Object table의 (obj_id)
            img (Image): Image table의 (img)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "UPDATE Image SET img=%s" \
                        "WHERE img_id=(SELECT img_id FROM Object WHERE obj_id=%s)"
                value = (img, obj_id)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_img_img_II(self, img_id, img) -> bool:
        """
        Image table의 (img) update

        Args:
            img_id (str): Image table의 (img_id)
            img (Image): Image table의 (img)

        Return:
            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "UPDATE Image SET img=%s WHERE img_id=%s"
                value = (img, img_id)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def update_mix_img_obj(self, iteration, img) -> bool:
        """
        Object table의 (cat_id)가 NULL이고, (iteration)이 iteration인 row를 찾음
        해당 row에서 (img_id)로 관계된 Image table의 (img)를 img로 업데이트

        Args:
            iteration : Object table의 (iteration)
            img(data) : Image table의 (img)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "UPDATE Image SET img=_binary%s " \
                        "WHERE img_id IN (SELECT img_id FROM Object WHERE iteration=%s AND cat_id IS NULL)"
                value = (img, iteration)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_object(self, img_id) -> bool:
        """
        Object table의 (img_id)를 받아
        해당하는 Object table의 모든 row를 삭제

        Args:
            img_id (str): Object table의 (img_id)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'DELETE FROM Object WHERE img_id=' + img_id
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_bbox(self, obj_id) -> bool:
        """
        Bbox table의 (obj_id)를 가지는 row 삭제

        Args:
            obj_id (str): Bbox table의 (obj_id)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'DELETE FROM Bbox WHERE obj_id=' + obj_id
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_mask(self, obj_id) -> bool:
        """
        Mask table의 (obj_id)를 가지는 모든 row 삭제

        Args:
            obj_id (str): Mask table의 (obj_id)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = 'DELETE FROM Mask WHERE obj_id=' + obj_id
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_bbox_img(self, img_id) -> bool:
        """
        Object table의 (img_id)를 통해 Object table의 (obj_id)를 가져옴
        이를통해 관계된 Bbox table의 (obj_id)를 가지는 모든 bbox 삭제

        Args:
            img_id (str): Object table의 (img_id)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "DELETE FROM Bbox WHERE " \
                        "obj_id IN (SELECT obj_id FROM Object WHERE img_id=%s)"
                value = (img_id)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_nomix_img(self, img_id) -> bool:
        """
        Object table의 (img_id)를 받아
        SuperCategory table의 (super_name)이 mix가 아닌 Object table의 row 삭제

        Args:
            img_id (str): Object table의 (img_id)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "DELETE FROM Object WHERE img_id=%s AND obj_id " \
                        "IN (SELECT obj_id FROM (SELECT obj_id FROM Object WHERE cat_id " \
                        "IN (SELECT cat_id FROM Category WHERE super_id " \
                        "IN (SELECT super_id FROM SuperCategory WHERE NOT super_name='mix'))) AS Obj)"

                value = (img_id)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_empty_obj(self):
        """
        Object tabel의 (cat_id), (img_id)가 둘다 (NULL)인
        Object table의 row 삭제

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "DELETE FROM Object WHERE cat_id IS NULL AND img_id IS NULL"
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_mix_obj(self, iteration) -> bool:
        """
        Grid table의 (width) x (height)가 (0) x (0)이고
        Object table의 (iteration)이 iteration인
        Object table의 rows 삭제

        Args:
            iteration (str) : Object table의 (iteration)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "DELETE FROM Object " \
                        "WHERE iteration=%s AND loc_id IN " \
                        "(SELECT loc_id FROM Location " \
                        "INNER JOIN (SELECT grid_id FROM Grid WHERE width=0 AND height=0) AS G " \
                        "ON G.grid_id=Location.grid_id)"
                value = (iteration)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def delete_img_TC(self, type, check_num):
        """
        Image table의 (type), (check_num)이
        type, check_num인 image table 삭제

        Args:
            type (str): Image table의 (type)
            check_num (str): Image table의 (check_num)

        Return:
            Bool: True
        """
        try:
            with self.db.cursor() as cursor:
                query = "DELETE FROM Image WHERE type=%s AND check_num=%s"
                value = (type, check_num)
                cursor.execute(query, value)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def get_aug_mask(self, grid_id, cat_id, aug_num):
        """
        Object table의 (cat_id), Location의 (grid_id)를 받아
        Location table의 (x), (y), Object table의 (iteration), Mask table의 (x), (y) 반환

        Args:
            grid_id (str): Grid table의 (grid_id)
            cat_id (str): Category table의 (cat_id)
            aug_num (str): Object table의 (aug_num)

        Return:
            tuple ((loc_x, loc_y, iteration, mask_id, mask_x, mask_y), (...))

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT Obj.loc_x, Obj.loc_y, Obj.iteration, Mask.mask_id, Mask.x, Mask.y " \
                        "FROM (SELECT O.obj_id, O.iteration, Loc.x AS loc_x, Loc.y AS loc_y " \
                        "      FROM (SELECT obj_id, iteration, loc_id FROM Object WHERE cat_id=%s AND aug_num=%s) AS O " \
                        "      INNER JOIN (SELECT x, y, loc_id FROM Location WHERE grid_id=%s) AS Loc " \
                        "      ON Loc.loc_id=O.loc_id) AS Obj " \
                        "INNER JOIN Mask ON Mask.obj_id=Obj.obj_id"
                value = (cat_id, aug_num, grid_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_aug_img(self, grid_id, cat_id, aug_num):
        """
        Object table의 (cat_id)와 Location table의 (grid_id)를 받아
        Location table의 (x), (y), Object table의 (iteration), Image table의 (img) 반환

        Args:
            grid_id (str): Grid table의 (grid_id)
            cat_id (str): Category table의 (cat_id)
            aug_num (str): Object table의 (aug_num)

        Return:
            tuple ()(): ((loc_x, loc_y, iteration, (byte)img), (...))

            None: 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT Obj.loc_x, Obj.loc_y, Obj.iteration, Image.img " \
                        "FROM (SELECT O.img_id, O.iteration, O.obj_id, Loc.loc_x, Loc.loc_y " \
                        "      FROM (SELECT obj_id, img_id, iteration, loc_id " \
                        "            FROM Object WHERE cat_id=%s AND aug_num=%s) AS O " \
                        "      INNER JOIN (SELECT x AS loc_x, y AS loc_y, loc_id " \
                        "                  FROM Location WHERE grid_id=%s) AS Loc " \
                        "      ON Loc.loc_id=O.loc_id) AS Obj " \
                        "INNER JOIN Image ON Image.img_id=Obj.img_id"
                value = (cat_id, aug_num, grid_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def get_aug_loc_id(self, grid_id):
        """
        Location table의 (grid_id)를 통해
        Location table의 (x), Location table의 (y), Location table의 (loc_id) 반환

        Args:
            grid_id (str): Location table의 (grid_id)

        Return:
            tuple()(): ((loc_x, loc_y, loc_id), (...))

            None: 조회된 값 없음

            False: 쿼리 실패
        """
        try:
            with self.db.cursor() as cursor:
                query = "SELECT x, y, loc_id FROM Location WHERE grid_id=%s"
                value = (grid_id)
                cursor.execute(query, value)
                v = cursor.fetchall()
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            if v:
                return v
            else:
                return None

    def set_obj_list(self, grid_id, cat_id, iteration, mix_num, aug_num='-1') -> bool:
        """
        Location table의 (grid_id)를 가진 row와
        Category table의 (cat_id)를 가진 row를 통해
        [Location table의 특정 (grid_id)를 가진 row 수] X
        [category table의 특정 (cat_id)를 가진 row 수] X
        [iteration]
        만큼 Object table에 row 생성

        dummy data이고 update될 data이기에 unique key 조건을 끔

        Args:
            grid_id (str): Location table의 (grid_id)
            cat_id (str): Category table의 (cat_id)
            iteration (str): Object table의 (iteration)
            mix_num (str): Object table의 (mix_num)
            aug_num (str): Object table의 (aug_num)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                # unique key 끄기
                query = "SET unique_checks = 0"
                cursor.execute(query)
                # tmp 임시 table 생성
                query = "CREATE TEMPORARY TABLE tmp(" \
                        "   img_id INT UNSIGNED," \
                        "   iteration INT UNSIGNED NOT NULL," \
                        "   mix_num INT NOT NULL," \
                        "   cat_id INT UNSIGNED NOT NULL," \
                        "   aug_num INT NOT NULL" \
                        ")"
                cursor.execute(query)
                # for문 이용해 tmp 테이블에 값을 채움
                for i in range(int(iteration)):
                    query = "INSERT INTO tmp(img_id, iteration, mix_num, cat_id, aug_num) " \
                            "VALUES(NULL, %s, %s, %s, %s)"
                    value = (i+1, mix_num, cat_id, aug_num)
                    cursor.execute(query, value)

                # main query
                query = "INSERT INTO Object(loc_id, cat_id, img_id, iteration, mix_num, aug_num) " \
                        "SELECT Obj.loc_id, Obj.cat_id, Obj.img_id, Obj.iteration, Obj.mix_num, Obj.aug_num " \
                        "FROM (SELECT * FROM tmp " \
                        "CROSS JOIN (SELECT loc_id FROM Location WHERE grid_id=%s) AS Loc) AS Obj"
                value = (grid_id)
                cursor.execute(query, value)

                # table id 변경
                # mysql의 autoincrement gap error 때문에 설정이 필요
                query = "SELECT MAX(obj_id) FROM Object"
                max_id = cursor.execute(query)
                query = "ALTER TABLE Object AUTO_INCREMENT = %s"
                value = (max_id)
                cursor.execute(query, value)
                # tmp table 삭제
                query = "DROP TABLE tmp"
                cursor.execute(query)

                # unique key 끄기
                query = "SET unique_checks = 0"
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_mix_obj_list(self, max_w, max_h, loc_id, iteration, mix_num, aug_num) -> bool:
        """
        Grid table의 [max_w] X [max_h] X [iteration] 만큼
        Object table에 row를 생성

        dummy data이고 update될 data이기에 unique key 조건을 끔

        Args:
            loc_id (str): Object table의 (loc_id)
            iteration (str): Object table의 (iteration)
            mix_num (str): Object table의 (mix_num)
            aug_num (str): Object table의 (aug_num)

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                # unique key 끄기
                query = "SET unique_checks = 0"
                cursor.execute(query)

                for j in range(int(max_w) * int(max_h)):
                    for iter in range(int(iteration)):
                        query = "INSERT INTO Object(img_id, loc_id, cat_id, iteration, mix_num, aug_num) " \
                                "VALUES(NULL, %s, NULL, %s, %s, %s)"
                        value = (loc_id, iter+1, mix_num, aug_num)
                        cursor.execute(query, value)

                # table id 변경
                # mysql의 autoincrement gap error 때문에 설정이 필요
                query = "SELECT MAX(obj_id) FROM Object"
                max_id = cursor.execute(query)
                query = "ALTER TABLE Object AUTO_INCREMENT = %s"
                value = (max_id)
                cursor.execute(query, value)

                # unique key 끄기
                query = "SET unique_checks = 0"
                cursor.execute(query)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_bulk_obj(self, datas) -> bool:
        """
        Object table에 여러 row 추가

        Args:
            datas (generator): ((img_id, loc_id, cat_id, iteration, mix_num), (...))

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "INSERT INTO Object (loc_id, cat_id, img_id, iteration, mix_num, aug_num) " \
                        "VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.executemany(query, datas)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_bulk_bbox(self, datas) -> bool:
        """
        Bbox table에 여러개의 row 추가

        Args:
            datas (generator) : ((obj_id, x, y, width, height), (...))

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "INSERT INTO Bbox (obj_id, x, y, width, height) " \
                        "VALUES (%s, %s, %s, %s, %s)"
                cursor.executemany(query, datas)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def set_bulk_img(self, datas) -> bool:
        """
        Image table에 여러개의 row 추가

        Args:
            datas (generator): ((env_id, img, type, check_num), (...))

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                query = "INSERT INTO Image (env_id, img, type, check_num) " \
                        "VALUES (%s, _binary%s, %s, %s)"
                cursor.executemany(query, datas)
        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def db_to_json(self, json_path, img_path, width=1290, height=1080, area=0):
        """
        DB의 전체 테이블에서 학습에 필요한 데이터들을 가져와
        json 타입으로 저장

        Args:
            json_path (str): json file 저장 경로
            img_path (str): img folder 경로

        Return:
            Bool: True or False

        """
        try:
            with self.db.cursor() as cursor:
                # coco format init
                coco_info = {"annotations": [],
                             "categories": [],
                             "images": []}

                # Image table의 모든 img를 img folder에 update
                # annotation의 images 정보 추가
                query = "SELECT img_id, img FROM Image"
                cursor.execute(query)
                img_table = cursor.fetchall()
                for row in img_table:
                    img_id, img = row[0], row[1]
                    save_img(byte_img=img,
                             img_dir=join(img_path, str(img_id) + '.jpg'))

                    img_dict = {}
                    img_dict["file_name"] = str(img_id) + '.jpg'
                    img_dict["height"] = height
                    img_dict["width"] = width
                    img_dict["id"] = img_id
                    coco_info["images"].append(img_dict)

                # Category table search
                query = "SELECT cat_id, super_id, cat_name FROM Category ORDER BY cat_id"
                cursor.execute(query)
                cat_table = cursor.fetchall()
                for iter, row in enumerate(cat_table):
                    cat_id, super_id, cat_name = row[0], row[1], row[2]
                    # SuperCategory table search
                    query = "SELECT super_name FROM SuperCategory WHERE super_id=%s"
                    value = (super_id)
                    cursor.execute(query, value)
                    super_name = sum(cursor.fetchall(), ())
                    coco_info["categories"].append({"id": iter + 1,
                                                    "name": cat_name,
                                                    "supercategory": super_name[0]})

                # Object table search
                query = "SELECT obj_id, cat_id, img_id FROM Object"
                cursor.execute(query)
                obj_table = cursor.fetchall()

                # annotations 정보
                for row in obj_table:
                    obj_id, cat_id, img_id = row[0], row[1], row[2]
                    anno_dict = {}
                    anno_dict["area"] = area
                    # Bbox table search
                    query = "SELECT x, y, width, height FROM Bbox WHERE obj_id=%s"
                    value = (obj_id)
                    cursor.execute(query, value)
                    bbox = list(sum(cursor.fetchall(), ()))
                    anno_dict["bbox"] = bbox
                    anno_dict["category_id"] = cat_id
                    anno_dict["id"] = obj_id
                    anno_dict["image_id"] = img_id
                    anno_dict["iscrowd"] = 0
                    # Mask table search
                    query = "SELECT x, y FROM Mask WHERE obj_id=%s"
                    value = (obj_id)
                    cursor.execute(query, value)
                    mask_table = cursor.fetchall()
                    mask = [list(sum(mask_table, ()))]
                    if mask[0]:
                        anno_dict["segmentation"] = mask
                    coco_info["annotations"].append(anno_dict)

                save_json(json_path=json_path, coco_format=coco_info)

        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True

    def db_to_json_type(self, json_path, img_path, type, width=1290, height=1080, area=0):
        """
        DB의 Image table에서 (type)이 type인 데이터들을 가져와
        json 타입으로 저장

        Args:
            json_path (str): json file 저장 경로
            img_path (str): img folder 경로
            type (str): Image table의 (type) -> 1: original, 2: mix, 3: synthesize

        Return:
            Bool: True or False
        """
        try:
            with self.db.cursor() as cursor:
                # coco format init
                coco_info = {"annotations": [],
                             "categories": [],
                             "images": []}

                # Image table의 모든 img를 img folder에 update
                # annotation의 images 정보 추가
                query = "SELECT img_id, img FROM Image WHERE type=%s"
                value = type
                cursor.execute(query, value)
                img_table = cursor.fetchall()
                for row in img_table:
                    img_id, img = row[0], row[1]
                    save_img(byte_img=img,
                             img_dir=join(img_path, str(img_id) + '.jpg'))

                    img_dict = {}
                    img_dict["file_name"] = str(img_id) + '.jpg'
                    img_dict["height"] = height
                    img_dict["width"] = width
                    img_dict["id"] = img_id
                    coco_info["images"].append(img_dict)

                # Category table search
                query = "SELECT cat_id, super_id, cat_name FROM Category ORDER BY cat_id"
                cursor.execute(query)
                cat_table = cursor.fetchall()
                for iter, row in enumerate(cat_table):
                    cat_id, super_id, cat_name = row[0], row[1], row[2]
                    # SuperCategory table search
                    query = "SELECT super_name FROM SuperCategory WHERE super_id=%s"
                    value = (super_id)
                    cursor.execute(query, value)
                    super_name = sum(cursor.fetchall(), ())
                    coco_info["categories"].append({"id": iter + 1,
                                                    "name": cat_name,
                                                    "supercategory": super_name[0]})

                # Object table search
                query = "SELECT Object.obj_id, Object.img_id, Object.cat_id FROM Object " \
                        "INNER JOIN (SELECT img_id FROM Image WHERE type=%s) AS I " \
                        "ON Object.img_id=I.img_id"
                value = (type)
                cursor.execute(query, value)
                obj_table = cursor.fetchall()

                # annotations 정보
                for row in obj_table:
                    obj_id, img_id, cat_id = row[0], row[1], row[2]
                    anno_dict = {}
                    anno_dict["area"] = area
                    # Bbox table search
                    query = "SELECT x, y, width, height FROM Bbox WHERE obj_id=%s"
                    value = (obj_id)
                    cursor.execute(query, value)
                    bbox = list(sum(cursor.fetchall(), ()))
                    anno_dict["bbox"] = bbox
                    anno_dict["category_id"] = cat_id
                    anno_dict["id"] = obj_id
                    anno_dict["image_id"] = img_id
                    anno_dict["iscrowd"] = 0
                    # Mask table search
                    query = "SELECT x, y FROM Mask WHERE obj_id=%s"
                    value = (obj_id)
                    cursor.execute(query, value)
                    mask_table = cursor.fetchall()
                    mask = [list(sum(mask_table, ()))]
                    if mask[0]:
                        anno_dict["segmentation"] = mask
                    coco_info["annotations"].append(anno_dict)

                save_json(json_path=json_path, coco_format=coco_info)

        except Exception as e:
            print('Error function:', inspect.stack()[0][3])
            print(e)
            self.db.rollback()
            return False
        else:
            self.db.commit()
            return True