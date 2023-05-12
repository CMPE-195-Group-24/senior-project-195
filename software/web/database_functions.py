import mysql.connector
import cursor

class Database:
    def __init__(self, user, host, database_name=None):
        self.user = user
        self.host = host
        self.database_name = database_name
        self.connection = None
        self.cursor = None
        
    def create_non_existing_database(self, password, database_name):
        self.connection = mysql.connector.connect(user=self.user, password=password, host=self.host)
        self.create_cursor_object()
        self.create_database(database_name)
        # self.disconnect_database()
        
    # Establishes the connection
    def connect_database(self, password, database_name=None):
        if database_name is None:
            print("No Database Exists")
            self.connection = mysql.connector.connect(user=self.user, password=password, host=self.host)
            self.create_cursor_object()
            self.create_database(database_name)
            print('Connected to Database:', self.connection)
        else:
            print("Database Exists: {}".format(self.database_name))
            self.connection = mysql.connector.connect(user=self.user, password=password, host=self.host, database=self.database_name)
            self.create_cursor_object()
            print('Connected to Database:', self.connection)

    # Creating a cursor object using the cursor() method
    def create_cursor_object(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    def create_database(self, new_database_name):
        #Doping database MYDATABASE if already exists.
        self.cursor.execute("DROP database IF EXISTS {}".format(new_database_name))

        #Preparing query to create a database
        sql = "CREATE database {}".format(new_database_name)
        #Creating a database
        self.cursor.execute(sql)
        self.database_name = new_database_name
        print("Created Database: {}".format(self.database_name))

    def create_table(self, table_name):
        #Dropping EMPLOYEE table if already exists.
        self.cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))
        #Creating table as per requirement
        sql = f'''CREATE TABLE {table_name}(
                ID INT NOT NULL, 
                USERNAME CHAR(100),
                EMAIL VARCHAR(100),
                FIRST_NAME CHAR(100),
                LAST_NAME CHAR(100),
                PASSWORD CHAR(100),
                ROLES CHAR(100),
                EVER_ADMIN BOOL,
                ACTIVE BOOL NOT NULL
                )'''
        self.cursor.execute(sql)
        print("Created Table:", table_name)

    def insert_into_table(self, table_name: str, id: int, username: str, email: str, first_name: str, last_name: str, password: str, roles: str):
        if (self.select_data(email)):
            print("ERROR: Email already exists.")
        else:
            # Preparing SQL query to INSERT a record into the database.
            # sql = f"""INSERT INTO {self.database_name}.{table_name} (ID, USERNAME, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, ROLES, IP, ACTIVE) VALUES
            #         ({id}, {username}, {email}, {first_name}, {last_name}, {password}, {roles}, '', false)
            #         """
            sql = f"""INSERT INTO SJSU.{table_name} (ID, USERNAME, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, ROLES, IP, ACTIVE) VALUES
                    ({id}, "{username}", "{email}", "{first_name}", "{last_name}", "{password}", "{roles}", "", 0)
                    """

            # try:
                # Executing the SQL command
            self.cursor.execute(sql)
            # Commit your changes in the database
            self.connection.commit()
            print(f"Inserted to Database: {self.database_name}")
            # except:
            #     # Rolling back in case of error
            #     self.connection.rollback()
            #     print(f"Failed to insert to Database: {self.database_name}")
                
        
    def update_active_status(self, table_name, id, active_status):
        #Preparing query to create a database
        sql = f""" UPDATE {self.database_name}.{table_name}
                SET ACTIVE = {active_status}
                WHERE ID = {id};
                """
        #Creating a database
        self.cursor.execute(sql)
        print("Updated table.")
        
    def update_password(self, table_name, id, password):
        #Preparing query to create a database
        sql = f""" UPDATE {self.database_name}.{table_name}
                SET PASSWORD = {password}
                WHERE ID = {id};
                """
        #Creating a database
        self.cursor.execute(sql)
        print("Updated table.")
        
    def select_data(self, email=None):
        sql = '''SELECT * from {}'''.format(self.database_name, f' {email}' if email is not None else '')
        #Executing the query
        self.cursor.execute(sql)
        if email is None:
            result = self.cursor.fetchall()
        else:
            result = self.cursor.fetchone()
        return result

    def show_all_databases(self):
        self.cursor.execute("SHOW DATABASES")
        print("All Databases:", self.cursor.fetchall())
    
    def show_tables_from_database(self):
        sql = f"SHOW TABLES FROM {self.database_name}"
        self.cursor.execute(sql)
        print("Tables:", self.cursor.fetchall())

    def drop_database(self, database_name):
        sql = f"DROP DATABASE IF EXISTS {database_name}"
        self.cursor.execute(sql)
        print("Dropped Database:", database_name)
        if self.database_name == database_name:
            self.database_name = None
        
    def show_all_columns(self, database_name, table_name):
        sql = f"DESCRIBE {database_name}.{table_name}"
        self.cursor.execute(sql)
        columns = self.cursor.fetchall()
        return columns
        # print("Column Format: (Field, Type, NULL, key, Default, Extra)")
        # print("Columns:", self.cursor.fetchall())
        # print("Columns:")
        # for column in columns:
        #     print("-", column[0])
    
    def show_contents_from_table(self, table_name):
        sql = f"SELECT * FROM {self.database_name}.{table_name}"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)
    
    def disconnect_database(self):
        #Closing the connection
        self.cursor.close()
        self.connection.close()
        print(f"Disconnected from database: {self.database_name}")