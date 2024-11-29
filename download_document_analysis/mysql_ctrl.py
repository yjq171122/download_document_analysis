# import pymysql
#
#
# class DatabaseConnection:
#     def __init__(self, host, user, password, database):
#         self.host = host
#         self.user = user
#         self.password = password
#         self.database = database
#         self.connection = None
#
#     def connect(self):
#         self.connection = pymysql.connect(
#             host=self.host,
#             user=self.user,
#             password=self.password,
#             database=self.database,
#             charset='utf8mb4',
#             cursorclass=pymysql.cursors.DictCursor
#         )
#         return self.connection
#
#     def close(self):
#         if self.connection:
#             self.connection.close()
#
#
# class DatabaseOperations:
#     def __init__(self, connection):
#         self.connection = connection
#
#     def execute_query(self, query, params=None):
#         with self.connection.connect() as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute(query, params)
#                 result = cursor.fetchall()
#         return result
#
#     def execute_command(self, command):
#         with self.connection.connect() as conn:
#             with conn.cursor() as cursor:
#                 cursor.execute(command)
#             conn.commit()
#
#     def get_single_row(self, query, params=None):
#         results = self.execute_query(query, params)
#         if results:
#             return results[0]
#         return None
#
#
# # 创建数据库连接对象
# connection = DatabaseConnection('localhost', 'root', '1234', 'database_ffff')
#
# # 创建数据库操作对象
# db_operations = DatabaseOperations(connection)

# # 执行查询并获取结果
# results = db_operations.execute_query('SELECT * FROM my_table')
# for row in results:
#     print(row)
#
# # 执行命令（例如插入、更新或删除）
# db_operations.execute_command('INSERT INTO my_table (column1, column2) VALUES (%s, %s)', ('value1', 'value2'))

# pip install mysql-connector-python
# pip install sqlalchemy

from sqlalchemy import create_engine, text
import pandas as pd
# from mysql_bd import ths_models

class MySQLMiddleware:
    def __init__(self, host="localhost", username="root", password="1234"):#, database="stock"):
        self.engine = create_engine(f"mysql+pymysql://{username}:{password}@{host}",echo=False)#/{database}",echo=False)

    #所有数据读取到pd
    def all_table_to_dataframe(self, table_name):
        try:
            df = pd.read_sql_table(table_name, self.engine)
            # print(f"Table {table_name} read into DataFrame successfully")
            return df
        except Exception as e:
            print(f"Error: {e}")

    #有条件数据读取到pd
    def query_table_to_dataframe(self,query):
        try:
            df = pd.read_sql_query(query, self.engine)
            # print(f"Table read into DataFrame successfully")
            return df
        except Exception as e:
            print(f"Error: {e}")

    def write_dataframe_to_table(self, df, table_name):
        try:
            df.to_sql(table_name, self.engine, if_exists='append', index=False) #append为追加  replace是覆盖
            # print(f"DataFrame written to table {table_name} successfully")
        except Exception as e:
            print(f"Error: {e}")

    def sql_ctrl(self,query):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                conn.commit()
            # print(f"语句执行成功")
            return result
        except Exception as e:
            print(f"语句执行错误: {e}")

    def update_table_data(self, table_name, update_dict, condition):
        """
        Update data in the specified table.

        Parameters:
        table_name (str): Name of the table to update.
        update_dict (dict): Dictionary of columns to update with new values.
        condition (str): Condition for the update (e.g., 'id = 1').
        """
        try:
            update_stmt = text(
                f"UPDATE {table_name} SET {', '.join([f'{k} = :{k}' for k in update_dict.keys()])} WHERE {condition}")
            with self.engine.connect() as conn:
                conn.execute(update_stmt, **update_dict)
            # print(f"Data in table {table_name} updated successfully")
        except Exception as e:
            print(f"Error updating data in table {table_name}: {e}")

    def delete_table_data(self, table_name, condition):
        """
        Delete data from the specified table.

        Parameters:
        table_name (str): Name of the table to delete from.
        condition (str): Condition for the deletion (e.g., 'id = 1').
        """
        try:
            delete_stmt = text(f"DELETE FROM {table_name} WHERE {condition}")
            with self.engine.connect() as conn:
                conn.execute(delete_stmt)
            # print(f"Data in table {table_name} deleted successfully")
        except Exception as e:
            print(f"Error deleting data from table {table_name}: {e}")

    def query_table_data(self, table_name, conditions=None):
        """
        根据条件查询表数据。

        Parameters:
        table_name (str): 表名。
        conditions (str or None): 查询条件，例如 'id > 10'。

        Returns:
        DataFrame: 查询结果。
        """
        try:
            if conditions:
                df = pd.read_sql_query(f"SELECT * FROM {table_name} WHERE {conditions}", self.engine)
            else:
                df = pd.read_sql_table(table_name, self.engine)
            # print(f"Table {table_name} data queried successfully")
            return df
        except Exception as e:
            print(f"Error querying data from table {table_name}: {e}")

    def delete_table_data_by_condition(self, table_name, condition):
        """
        根据条件删除表数据。

        Parameters:
        table_name (str): 表名。
        condition (str): 删除条件，例如 'id = 1'。
        """
        try:
            delete_stmt = text(f"DELETE FROM {table_name} WHERE {condition}")
            with self.engine.connect() as conn:
                conn.execute(delete_stmt)
            # print(f"Data in table {table_name} deleted successfully by condition")
        except Exception as e:
            print(f"Error deleting data from table {table_name}: {e}")

    def update_table_data_by_condition(self, table_name, update_dict, condition):
        """
        根据条件修改表数据。

        Parameters:
        table_name (str): 表名。
        update_dict (dict): 要更新的列名和对应的新值。
        condition (str): 修改条件，例如 'id = 1'。
        """
        try:
            # 构建更新SQL语句，使用命名参数
            set_clause = ', '.join([f"{key} = :{key}" for key in update_dict.keys()])
            update_stmt = text(f"UPDATE {table_name} SET {set_clause} WHERE {condition}")
            with self.engine.connect() as conn:
                # 使用字典来绑定参数
                conn.execute(update_stmt, update_dict)
                conn.commit()
                print(update_stmt)
            # print(f"Data in table {table_name} updated successfully by condition")
        except Exception as e:
            print(f"Error updating data in table {table_name}: {e}")

        # Example usage:
if __name__ == "__main__":
    # Initialize MySQLMiddleware object
    middleware = MySQLMiddleware()
    #     host="localhost",
    #     username="root",
    #     password="1234",
    #     database="stock"
    # )

    # Example: read table data into DataFrame
    # df = middleware.all_table_to_dataframe("ths_concept")
    # print("DataFrame from table:")
    # print(df)
    # df = middleware.sql_ctrl("INSERT INTO concept_stock  VALUES ('1', '张三', '20');")
    # middleware.sql_ctrl("update concept_stock set stock_code = '11' where stock_code = '1'")
    # middleware.sql_ctrl("delete from concept_stock where stock_code = '300347' and concept_code = 'M';delete from concept_stock where stock_code = '301333' and concept_code = 'M';delete from concept_stock where stock_code = '688293' and concept_code = 'M';")
    # df = middleware.query_table_to_dataframe("select * from concept_stock")
    # print(df)
    #
    # # Example: write DataFrame to table
    # new_df = pd.DataFrame({'id': [4, 2, 3], 'name': ['John555', 'Doe', 'Jane']})
    # middleware.write_dataframe_to_table(new_df, "new_test_table")
    #
    # # 更新表数据
    # update_dict = {'column1': 'new_value1', 'column2': 'new_value2'}
    # middleware.update_table_data('my_table', update_dict, 'id = 1')
    #
    # # 删除表数据
    # middleware.delete_table_data('my_table', 'id = 2')
    #
    # # 写入新的DataFrame数据到表
    # new_df = pd.DataFrame({'column1': ['value3'], 'column2': ['value4']})
    # middleware.write_dataframe_to_table(new_df, 'my_table')

    # # 根据条件查询数据
    # conditions = "id > 1"
    # df = middleware.query_table_data('new_test_table', conditions)
    # print(df)
    #
    # # 根据条件修改数据
    # update_dict = {'name': 'ccccccccccccccccccc'}
    # condition = "id = 3"
    # middleware.update_table_data_by_condition('new_test_table', update_dict, condition)

    # # 根据条件删除数据
    # condition = "id = 6"
    # middleware.delete_table_data_by_condition('my_table', condition)

