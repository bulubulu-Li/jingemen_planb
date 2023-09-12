# pip3 install PyMysql
import pymysql
import json
import datetime

class MysqlHelper():
    def __init__(self, config):
        self.config = config
    
    def connect(self, try_number = 3):
        try:
            self.db = pymysql.connect(host=self.config["host"],
                            port=self.config["port"],
                            user=self.config["user"],
                    password=self.config["password"],
                    database=self.config["database"])
        except Exception as e:
            print("connect ERROR: {}".format(e))
            if try_number > 0:
                self.connect(try_number=try_number - 1)
            else:
                import sys
                sys.exit()
        else:
            print("connect success")

        
    def search(self, sql, try_number = 3):
        try:
            cursor = self.db.cursor()
            # cursor.execute("select * from users")
            cursor.execute(sql)
            data = cursor.fetchall()
        except Exception as e:
            print("search ERROR: {}".format(e))
            if try_number > 0:
                self.connect(try_number=try_number - 1)
                data = self.search(sql, try_number=try_number - 1)
        return data
    
    def searchDict(self, sql, try_number=3):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = {}
                for i in range(len(columns)):
                    result[columns[i]] = row[i]
                results.append(result)
        except Exception as e:
            print("searchDict ERROR: {}".format(e))
            if try_number > 0:
                self.connect(try_number=try_number - 1)
                results = self.searchDict(sql, try_number=try_number - 1)
        return results
    
    def update(self, sql, try_number = 3):
        try:
            cursor = self.db.cursor()
            # cursor.execute("select * from users")
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("search ERROR: {}".format(e))
            self.db.rollback()
            if try_number > 0:
                self.connect(try_number=try_number - 1)
                data = self.search(sql, try_number=try_number - 1)
        return data
    
    def print_first_row(self, table_name,try_number = 3):
        try:
            cursor = self.db.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            columns = [column[0] for column in cursor.description]
            data = cursor.fetchone()
            print(f"{table_name}:")
            print(columns)
            print(data)
        except Exception as e:
            print(f"ERROR: {e}")
            if try_number > 0:
                self.connect(try_number=try_number - 1)
                self.print_first_row(table_name, try_number=try_number - 1)



if __name__ == "__main__":
    config = {"host":'8.217.5.212',
              "port":3306,
              "user":'assistant',
              "password":'kuaijie2023',
              "database":'test'}
    mysql = MysqlHelper(config)
    # print(mysql.search("SELECT * FROM knowledgefile WHERE isValid=TRUE"))
    data=mysql.searchDict("SELECT * FROM knowledgepair WHERE state=10002")
    # Convert datetime objects to strings
    for d in data:
        for k, v in d.items():
            if isinstance(v, datetime.datetime):
                d[k] = str(v)
    print(data)
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    # extract files using the same method
    data=mysql.searchDict("SELECT * FROM knowledgefile WHERE isValid=TRUE")
    # Convert datetime objects to strings
    for d in data:
        for k, v in d.items():
            if isinstance(v, datetime.datetime):
                d[k] = str(v)
    print(data)
    with open('files.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # qa_list = [{'question': d['question'], 'answer': d['answer']} for d in data]
    # # 输入到一个json文件中

    # with open('qa.json', 'w', encoding='utf-8') as f:
    #     json.dump(qa_list, f, ensure_ascii=False, indent=4)

    # print(mysql.search("SELECT COUNT(*) FROM knowledgefile WHERE isValid=TRUE"))
    # mysql.print_first_row("SELECT COUNT(*) FROM knowledgefile WHERE isValid=TRUE;")