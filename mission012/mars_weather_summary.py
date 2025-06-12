import mysql.connector

# MySQL 연결 및 Query 실행을 수행하는 Helper 클래스.
class MySQLHelper():
    def __init__(self, host, user, password, database):
        '''
        (선택) DB 연결 정보에 대한 초기화 진행.
        '''
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._connection = None

    # DB 연결 상태를 확인하는 함수.
    def _check_connect_db(self):
        # DB 연결 상태 확인.
        if self._connection and self._connection.is_connected():
            print('_check_connect_db: 이미 연결된 상태입니다.')
            return True
        else:
            print('_check_connect_db: DB 연결이 필요합니다.')
            return False

    # DB 연결을 수행하는 함수.
    def connect_db(self):
        '''
        Args:
            None.
        Returns:
            bool: 연결 상태에 따른 실행 유무를 Boolean 반환.
        '''
        # DB 연결 상태 확인.
        self._check_connect_db()
        
        try:
            # MySQL Server 연결을 위한 매개변수 Dict.
            connection_args = {
                'host': self._host,
                'user': self._user,
                'password': self._password
            }
            # 사용하고자 하는 DB 이름이 지정된 경우 Dict args 수정.
            if self._database:
                connection_args['database'] = self._database
            
            # Unpacking connection_args.
            self._connection = mysql.connector.connect(**connection_args)
            
            # DB 연결 상태 확인.
            if self._connection.is_connected():
                # MySQL Server 및 DB 모두 연결되었을 경우,
                if self._database:
                    print(f'connect_db: MySQL Server의 "{self._database}" DB에 성공적으로 연결되었습니다.')
                # MySQL Server만 연결되었을 경우,
                else:
                    print('connect_db: MySQL Server에 성공적으로 연결되었습니다.')
                # 연결 성공 시 True 반환.
                return True
            else:
                print('connect_db: MySQL Server에 연결되었지만 활성화되지 않았습니다.')
                self._connection = None # 초기화.
                return False
        except mysql.connector.Error as error:
            # ERROR 1049는 'ER_BAD_DB_ERROR'.
            if self._database and error.errno == 1049:
                print(f'connect_db: DB "{self._database}"가 존재하지 않습니다.')
                print('connect_db: DB 생성 시도 중...')
                # DB 생성 시도.
                if self._create_db(connection_args):
                    print(f'connect_db: DB "{self._database}" 생성에 성공했습니다.')
                    # 생성된 DB로 연결 재시도.
                    return self._reconnect_db(connection_args)
                else:
                    print(f'connect_db: DB "{self._database}" 생성에 실패했습니다.')
                    self._connection = None
                    return False
            # 다른 종류의 오류 발생.
            else:
                print(f'connect_db: DB 연결에 오류가 발생했습니다: {error}')
                self._connection = None
                return False

    # 지정된 이름으로 DB를 생성하는 함수.
    def _create_db(self):
        '''
        Args:
            None.
        Returns:
            bool: DB 생성에 성공 유무를 bool로 반환.
        '''
        connection_args = None

        try:
            # MySQL Server 연결을 위한 매개변수 Dict.
            connection_args = {
                'host': self._host,
                'user': self._user,
                'password': self._password
            }
            # MySQL Server만 연결.
            temp_connect = mysql.connector.connect(**connection_args)
            
            # DB 연결 상태 확인.
            if temp_connect.is_connected():
                cursor = temp_connect.cursor()
                create_db_query = f'CREATE DATABASE IF NOT EXISTS {connection_args['database']};'
                # Query 실행 및 반영.
                cursor.execute(create_db_query)
                temp_connect.commit()
                cursor.close()
                # DB 생성 성공 시 True 반환.
                return True
            else:
                print('_create_db: MySQL Server 연결에 실패했습니다.')
                return False
        except mysql.connector.Error as error:
            print(f'_create_db: DB 생성 중 오류가 발생했습니다: {error}')
            return False
        finally:
            if temp_connect and temp_connect.is_connected():
                temp_connect.close()
    
    # 생성한 DB로 연결을 재시도하는 함수.
    def _reconnect_db(self, con_args):
        '''
        Args:
            con_args (Dict): MySQL 연결을 위한 매개변수 Dict.
        Returns:
            bool: 재연결 유무를 확인하기 위한 Boolean 반환.
        '''
        try:
            # con_args 내 database 변수가 존재하지 않으면 False 반환.
            if not con_args['database']:
                return False
            
            # MySQL Server 및 DB 연결.
            self._connection = mysql.connector.connect(**con_args)
            # DB 연결 상태 확인.
            if self._connection.is_connected():
                print(f'_reconnect_db: MySQL Server에 "{self._database}" DB를 생성하고 성공적으로 연결되었습니다.')
                return True
            else:
                print('_reconnect_db: MySQL Server에 연결되었지만 활성화되지 않았습니다.')
                return False
        except mysql.connector.Error as error:
            print(f'_reconnect_db: DB 생성 후 연결 중 오류가 발생했습니다: {error}')
            self._connection = None
            return False

    # DB 연결을 종료하는 함수.
    def disconnect_db(self):
        '''
        Args:
            None.
        Returns:
            None.
        '''
        if self._check_connect_db():
            self._connection.close()
            print('disconnect_db: MySQL Server를 종료합니다.')
        self._connection = None # 초기화.

    # 테이블이 존재하는지 확인하는 함수.
    def check_table(self, table_name):
        '''
        Args:
            table_name (str): 확인하고자 하는 테이블의 이름.
        Returns:
            bool: 테이블의 존재 유무를 Boolean으로 반환.
        '''
        # DB 연결 확인.
        self._check_connect_db()
        
        cursor = None
        
        try:
            cursor = self._connection.cursor()
            # information_schema.talbes를 사용하여 테이블의 존재 유무 확인.
            check_query = '''
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = %s
            ) AS table_exists;
            '''
            cursor.execute(check_query, (self._database, table_name))
            result = cursor.fetchone()
            if result and result[0] == 1:
                print(f'check_table: DB 내 "{table_name}" 테이블이 존재합니다.')
                return True
            print(f'check_table: DB 내 "{table_name}" 테이블이 존재하지 않습니다.')
            return False
        except mysql.connector.Error as error:
            print(f'check_table: DB의 테이블 확인 중 오류가 발생했습니다: {error}')
            return False
        finally:
            if cursor:
                cursor.close()

    # 테이블의 컬럼명과 데이터 타입을 추출하는 함수.
    def _extract_table_info(self, table_name):
        '''
        Args:
            table_name: 정보를 추출하고자 하는 테이블 이름.
        Returns:
            list: 테이블의 컬럼명과 데이터 타입이 기록된 튜플 리스트.
        '''
        # DB 연결 상태 확인.
        self._check_connect_db()
        
        cursor = None
        table_info = []
        
        try:
            cursor = self._connection.cursor()
            # information_schema.columns를 사용하여 테이블 조회.
            query = '''
            SELECT COLUMN_NAME, DATA_TYPE
            FROM information_schema.columns
            WHERE table_schema = %s
            AND table_name = %s
            ORDER BY ORDINAL_POSITION;
            '''
            cursor.execute(query, (self._database, table_name))
            
            # 결과의 각 행에서 컬럼명과 데이터 타입 추출.
            for row in cursor.fetchall():
                table_info.append((row[0], row[1]))
            # 추출한 튜플 리스트 반환.
            return table_info
        except mysql.connector.Error as error:
            print(f'"{table_name}" 테이블의 정보 추출 중 오류가 발생했습니다: {error}')
            return []
        finally:
            if cursor:
                cursor.close()

    # csv 파일을 읽고, 지정한 테이블에 저장하는 함수.
    def extract_csv_info(self, csv_path, table_name):
        '''
        Args:
            csv_path: 저장하고자 하는 데이터가 포함된 csv 파일 경로.
            table_name: 저장하고자 하는 테이블의 이름.
        Returns:
            list: query 생성에 필요한 리스트.
        '''
        # 지정된 테이블의 정보 수집.
        table_info = self._extract_table_info(table_name)
        csv_info = []
        
        print(f'extract_csv_info: {table_info}')
        print(f'extract_csv_info: {csv_info}')

    # Query 실행 및 결과를 반환하는 함수.
    def execute_query(self, query, parms = None):
        '''
        Args:
            query (str): 실행하고자 하는 SQL Query 문자열.
            parms (tuple, optional): Query에 바인딩할 매개변수 튜플 (기본값: None)
        Returns:
            bool: Query 실행의 성공 유무를 Boolean으로 반환.
        '''
        # DB 연결 확인.
        self._check_connect_db()
        
        cursor = None
        
        try:
            cursor = self._connection.cursor()
            cursor.execute(query, parms or ())
            self._connection.commit()
            print(f'execute_query: Query 실행에 성공했습니다.\n{query}')
            return True
        except mysql.connector.Error as error:
            print(f'execute_query: Query 실행 중 오류가 발생했습니다: {error}\n{query}')
            if self._connection:
                self._connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

# 실행 함수.
def main():
    # MySQL config.
    config_db = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': 'root',
        'database': 'mars_mission'
    }
    
    # MySQLHelper 인스턴스 생성.
    sql_helper = MySQLHelper(**config_db)

    # MySQL Server 및 DB 연결 시도.
    if sql_helper.connect_db():
        table_name = 'mars_weather'
        # 테이블 조회.
        if not sql_helper.check_table(table_name):
            print(f'main: DB 내 "{table_name}" 테이블 생성 중...')
            # CREATE TABLE Query.
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS mars_weather(
                weather_id INT PRIMARY KEY AUTO_INCREMENT,
                mars_date DATETIME,
                temp INT,
                storm INT
            )
            '''
            # Query 실행 및 성공 유무 확인.
            if sql_helper.execute_query(create_table_query):
                print('Query 실행에 성공했습니다.')
            else:
                print('Query 실행에 실패했습니다.')
        
        csv_path = 'mission/csv/mars_weathers_data.csv'
        # csv 파일 조회.
        sql_helper.extract_csv_info(csv_path, table_name)
    
    # DB 연결 종료.
    sql_helper.disconnect_db()

# 코드 실행.
if __name__ == '__main__':
    main()