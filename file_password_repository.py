from multiprocessing.synchronize import Lock

from signum.password_repository import PasswordRepository
import multiprocessing

from tinydb import TinyDB, where


class FilePasswordRepository(PasswordRepository):
    def __init__(self, username_hash_salt: str, password_repository_file_path: str):
        super().__init__(username_hash_salt)
        self.__database: TinyDB = TinyDB(password_repository_file_path)
        self.__lock: Lock = multiprocessing.Lock()

    def _save_password(self, username: str, password: str) -> None:
        with self.__lock:
            self.__database.upsert({'username': username, "password": password}, where('username') == username)

    def _load_password(self, username: str) -> str:
        with self.__lock:
            record = self.__database.get(where('username') == username)

            if record:
                return record["password"]

            return ""
