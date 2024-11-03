from sqlalchemy import create_engine
import psycopg2
from dotenv import load_dotenv
import os


class Postgres:
    def __init__(self, db_name):
        load_dotenv()
        self.connect(db_name)

    def connect(self, db_name):
        # DB 연결 설정
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        DB_USER = os.getenv('DB_USER')
        DB_PASS = os.getenv('DB_PASS')
        DB_NAME = db_name

        # SQLAlchemy 엔진 생성 (MariaDB용)
        self.engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

        # pymysql 연결
        self.conn = psycopg2.connect(
            host=DB_HOST, 
            port=DB_PORT, 
            user=DB_USER, 
            password=DB_PASS, 
            dbname=DB_NAME
        )
        self.cursor = self.conn.cursor()

    def check_table_exists(self, schema_name, table_name):
        # 테이블 존재 여부 확인 쿼리
        self.cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE  table_schema = %s
                AND    table_name   = %s
            );
        """, (schema_name, table_name))
        return self.cursor.fetchone()[0]

    def string_escape(self, str):
        return str.replace("'", "''")
    
    def disconnect(self):
        # psycopg2 연결 종료
        if self.conn:
            self.conn.close()
        # SQLAlchemy 엔진 연결 종료
        if self.engine:
            self.engine.dispose()

    def create_table(self):
        # naver_search 테이블 생성
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS naver_search (
                id SERIAL PRIMARY KEY,
                text TEXT,
                images TEXT,
                title TEXT,
                link TEXT,
                bloggername TEXT,
                postdate DATE
            )
        ''')

    def insert_by_dict(self, tname, data):
        keys = data.keys()
        columns = ', '.join(keys)
        values = ", ".join(["%s"] * len(data))

        # 데이터 삽입
        sql = f'''
        INSERT INTO {tname} ({columns})
        VALUES ({values})
        '''
        self.cursor.execute(sql, tuple([data[key] for key in keys]))
        self.conn.commit()

    def insert_by_series(self, tname, data):
        columns = ', '.join(['`' + x + '`' for x in data.index])
        values = ", ".join(["%s"] * data.shape[0])

        # 데이터 삽입
        sql = f'''
        INSERT INTO {tname} ({columns})
        VALUES ({values})
        '''
        self.cursor.execute(sql, tuple(data.values))
        self.conn.commit()

    def insert_data(self, data):
        link = data['link']
        if link:
            self.cursor.execute(f"SELECT 1 FROM naver_search WHERE link = %s", (link,))
            if self.cursor.fetchone():
                return

        # 문자열 형태의 날짜를 datetime 객체로 변환
        # postdate = datetime.strptime(data['postdate'], '%Y%m%d')

        # 데이터 삽입
        self.cursor.execute('''
        INSERT INTO naver_search (text, images, title, link, topic, bloggername, postdate)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (data['text'], ';'.join(data['images']), data['title'], data['link'], data['topic'], data['bloggername'], data['postdate']))
        self.conn.commit()

    def create_or_append_table(self, schema, table_name, df):
        table_full_name = f'"{schema}"."{table_name}"'
        # 테이블 존재 여부 확인
        self.cursor.execute(f"SELECT to_regclass('{table_full_name}');")
        exists = self.cursor.fetchone()[0]

        if not exists:
            # 테이블이 존재하지 않으면 생성
            create_table_query = f'''
            CREATE TABLE {table_full_name} (
                time TIMESTAMP PRIMARY KEY,
                open DOUBLE PRECISION,
                high DOUBLE PRECISION,
                low DOUBLE PRECISION,
                close DOUBLE PRECISION,
                volume DOUBLE PRECISION,
                quote_asset_volume DOUBLE PRECISION,
                n_trade DOUBLE PRECISION,
                take_buy_base_asset_volume DOUBLE PRECISION,
                take_buy_quote_asset_volume DOUBLE PRECISION
            );
            '''
            self.cursor.execute(create_table_query)
            self.conn.commit()
            print(f"Table {table_full_name} created.")

        # DataFrame을 사용하여 데이터 추가
        df.to_sql(table_name, self.engine, schema=schema, if_exists='append', index=False)
        print(f"Data appended to {table_full_name}.")