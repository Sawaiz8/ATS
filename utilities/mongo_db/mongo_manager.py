from pymongo import MongoClient
from typing import List, Dict
import os

class MongoDBManager:
    def __init__(self, uri=os.getenv("MONGO_URL"), db_name=os.getenv("MONGO_INITDB_DATABASE")):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.students_data_collection = None
        self.volunteer_data_collection = None
        self.sessions_data_collection = None

    def connect(self):
        # Connect to MongoDB
        self.client = MongoClient(self.uri)
        # Access the database
        self.db = self.client[self.db_name]
        self.students_data_collection = self.db["students"]
        self.volunteer_data_collection = self.db["volunteers"]
        self.sessions_data_collection = self.db["sessions"]
        
    def disconnect(self)-> None:
        if self.client:
            self.client.close()
        self.client = None
        self.db = None
        self.students_data_collection = None
        self.volunteer_data_collection = None
        self.sessions_data_collection = None
        
    def db_connection(func):
        async def wrapper(self, *args, **kwargs):
            self.connect()
            try:
                result = await func(self, *args, **kwargs)
            finally:
                self.disconnect()
            return result
        return wrapper

    @db_connection
    async def upsert_student_data(self, student_data) -> None:
        # Get the current max student_id and increment by 1
        max_student = self.students_data_collection.find_one(
            sort=[("student_id", -1)]
        )
        next_id = 1 if max_student is None else max_student["student_id"] + 1
        
        # Set the auto-generated ID
        student_data["student_id"] = next_id
        
        self.students_data_collection.update_one(
            {"student_id": student_data["student_id"]},
            {"$set": student_data},
            upsert=True
        )

    @db_connection
    async def upsert_volunteer_data(self, volunteer_data: Dict) -> None:
        # Get the current max volunteer_id and increment by 1
        max_volunteer = self.volunteer_data_collection.find_one(
            sort=[("volunteer_id", -1)]
        )
        next_id = 1 if max_volunteer is None else max_volunteer["volunteer_id"] + 1
        
        # Set the auto-generated ID
        volunteer_data["volunteer_id"] = next_id
        
        self.volunteer_data_collection.update_one(
            {"volunteer_id": volunteer_data["volunteer_id"]},
            {"$set": volunteer_data},
            upsert=True
        )
    
    @db_connection
    async def upsert_session_data(self, session_data: Dict) -> None:
        # Get the current max session_id and increment by 1
        max_session = self.sessions_data_collection.find_one(
            sort=[("session_id", -1)]
        )
        next_id = 1 if max_session is None else max_session["session_id"] + 1
        
        # Set the auto-generated ID
        session_data["session_id"] = next_id
        
        self.sessions_data_collection.update_one(
            {"session_id": session_data["session_id"]},
            {"$set": session_data},
            upsert=True
        )
    
    @db_connection
    async def get_all_session_names(self) -> List[str]:
        session_names = list(self.sessions_data_collection.distinct("session_name"))
        return session_names if session_names else []
    
    @db_connection
    async def get_section_names(self, session_name: str) -> List[str]:
        session = self.sessions_data_collection.find_one({"session_name": session_name})
        sections = [section["section_name"] for section in session.get("sections", [])] if session else []
        return sections
    
    @db_connection
    async def get_students_by_session_and_section(self, session_name: str, section_name: str) -> List[Dict]:
        students = list(self.students_data_collection.find({
            "session_name": session_name,
            "section_name": section_name
        }))
        return students if students else []


    @db_connection
    async def delete_session_data(self, session_name: str) -> None:
        # Delete the session document
        self.sessions_data_collection.delete_one({"session_name": session_name})
        # Delete all students associated with the session
        self.students_data_collection.delete_many({"session_name": session_name})

    @db_connection
    async def update_student_fields(self, session_name: str, section_name: str, student_id: int, update_fields: Dict) -> None:
        """
        Update individual fields for a student document.
        :param session_name: The name of the session the student belongs to.
        :param section_name: The name of the section the student belongs to.
        :param student_id: The ID of the student to update.
        :param update_fields: A dictionary of fields to update.
        """
        self.students_data_collection.update_one(
            {
                "session_name": session_name,
                "section_name": section_name,
                "student_id": student_id
            },
            {"$set": update_fields}
        )

