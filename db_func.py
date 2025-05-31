from contextlib import contextmanager
import psycopg2 as ps
from champion import Champion
from init_config import config


class DBManager:
    def __init__(self, schema: str, db_conn: dict):
        """
        Manages interactions with database

        :param schema: schema to use in the database
        :param db_conn: connection parameters for connecting to the database
        """
        self.schema = schema
        self.db_conn = db_conn


    @contextmanager
    def get_cursor(self):
        """
        Context manager to yield a database cursor, automatically committing changes
        """
        try:
            with ps.connect(**self.db_conn) as conn:
                with conn.cursor() as cursor:
                    yield cursor
                    conn.commit()
        except Exception as e:
            print(f"Database error: {e}")


    def get_pass(self, username: str):
        """
        Retrieve the hashed password for a user from the database

        :param username: username whose password needs to be fetched
        :return: hashed password if found, None if not found
        """
        try:
            with self.get_cursor() as cursor:
                    query = f"select password_hash from {self.schema}.users where username = %s"
                    cursor.execute(query, (username,))
                    response = cursor.fetchone()
                    return response[0] if response else None

        except Exception as e:
            print(f"Failed to get password: {e}")
            return None


    def update_pass(self, username: str, new_passw: str):
        """
        Update the password for a specific user

        :param username: username whose password is being updated
        :param new_passw: new hashed password to store in the database
        """
        try:
            with self.get_cursor() as cursor:
                    sql_query = f"update {self.schema}.users set password_hash = %s where username = %s"
                    cursor.execute(sql_query, (new_passw, username))

        except Exception as e:
            print(f"Failed to update password: {e}")
            return None


    def add_user(self, username:str, email: str, passw: str):
        """
        Add a new user to database and creates an entry for that user in the user_builds table

        :param username: username of the new user
        :param email: email address of the new user
        :param passw: hashed password of the new user
        :return: True if the operations were successful, False otherwise
        """
        try:
            with self.get_cursor() as cursor:
                    insert_query = f"insert into {self.schema}.users (username, email, password_hash) values (%s, %s, %s) returning id"
                    cursor.execute(insert_query, (username, email, passw))
                    user_id = cursor.fetchone()[0]
                    insert_build_query = f"insert into {self.schema}.user_builds (user_id, champions) values (%s, ' ')"
                    cursor.execute(insert_build_query, (user_id,))
                    print("Account created successfully!")
                    return True, cursor.statusmessage

        except Exception as e:
            print(f"Failed to create account: {e}")
            return False, f"Unsuccessful query execution: {e}"


    def delete_user(self, username: str):
        """
        Delete user from database

        :param username:  username of the user to be deleted
        """
        try:
            with self.get_cursor() as cursor:
                    sql_query = f"delete from {self.schema}.users where username = %s"
                    cursor.execute(sql_query, (username,))

        except Exception as e:
            print(f"Failed to delete account: {e}")
            return None


    def email_exists(self, email: str):
        with self.get_cursor() as cursor:
            query = f"SELECT COUNT(*) FROM {self.schema}.users WHERE email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return result[0] > 0


    def user_exists(self, username: str):
        with self.get_cursor() as cursor:
            query = f"SELECT COUNT(*) FROM {self.schema}.users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return result[0] > 0


    def read_build(self, champion: Champion):
        """
        Retrieve build data for a specific champion

        :param champion: champion object containing the champion's name
        :return: build data of the champion if found, None if not found
        """
        try:
            with self.get_cursor() as cursor:
                    query = f"select * from {self.schema}.builds where champion_name = %s"
                    cursor.execute(query, (champion,))
                    row = cursor.fetchone()
                    if row:
                        columns = [desc[0] for desc in cursor.description]
                        return dict(zip(columns, row))
            return None

        except Exception as e:
            print(f"Failed to read build: {e}")
            return None


    def save_champ_build(self, champion: str, username: str):
        """
        Save a champion's build for a specific user

        :param champion: name of the champion to save
        :param username: username of the user saving the build
        :return:
        """
        try:
            with self.get_cursor() as cursor:
                    query = f""" UPDATE {self.schema}.user_builds SET champions = champions || ' ' || %s
                            WHERE user_id = (SELECT id FROM {self.schema}.users WHERE username = %s)"""
                    cursor.execute(query, (champion, username))
                    return True, "Build saved successfully."

        except Exception as e:
            print(f"Failed to save build: {e}")
            return False, f"Unsuccessful query execution: {e}"


    def get_saved_builds(self, username = str):
        try:
            with self.get_cursor() as cursor:
                    query = f"select champions from {self.schema}.user_builds where user_id = (SELECT id FROM {self.schema}.users WHERE username = %s)"
                    cursor.execute(query, (username, ))
                    result = cursor.fetchone()
                    return result

        except Exception as e:
            print(f"Failed to get saved builds: {e}")
            return False, f"Unsuccessful query execution: {e}"


    def search_champions(self, search: str):
        """
        Search for champions in the database that match the given search query

        :param search: search query to match against champion names
        :return: list of champion names that match the search query
        """
        try:
            with self.get_cursor() as cursor:
                    query = f"select champion_name from {self.schema}.builds where lower(champion_name) like %s"
                    cursor.execute(query, (search + '%',))
                    return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            print(f"Search error: {e}")
            return []


db_manager = DBManager(
    schema=config['database']['schema'],
    db_conn=config['database']['database_config']
)