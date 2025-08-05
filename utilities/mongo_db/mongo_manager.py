from pymongo import MongoClient
from typing import List, Dict
import os

class MongoDBManager:
    def __init__(self, uri=os.getenv("MONGO_DB_ATLAS_URI"), db_name=os.getenv("MONGO_INITDB_DATABASE")):
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
    async def upsert_volunteer_data(self, volunteer_data: Dict) -> None:
        # Upsert using email as the primary key
        self.volunteer_data_collection.update_one(
            {"email": volunteer_data["email"]},
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
    async def get_session_data(self, session_name: str) -> Dict:
        session_data = self.sessions_data_collection.find_one({"session_name": session_name})
        return session_data if session_data else {}
    
    # @db_connection
    # async def get_volunteer_data(self, session_name: str, category: str) -> Dict:
    #     volunteer_data = self.volunteer_data_collection.find_one({"session_name": session_name, "category": category.upper()})
    #     return volunteer_data if volunteer_data else {}
    
    @db_connection
    async def get_all_volunteers_data(self, session_name: str, category: str) -> List[Dict]:
        # Find all volunteers matching the session and category
        cursor = self.volunteer_data_collection.find(
            {"session_name": session_name, "category": category}
        )

        # Convert cursor to list of dictionaries
        volunteer_data = list(cursor)
        return volunteer_data if volunteer_data else []
    
    @db_connection
    async def update_volunteer_status(self, name: str, email: str, new_status: str) -> bool:
        """
        Update the applicant_status for a volunteer matching the given name, phone and email.
        
        Args:
            name: Name of the volunteer
            phone_number: Phone number of the volunteer 
            email: Email of the volunteer
            new_status: New status to set for the volunteer
            
        Returns:
            bool: True if update was successful, False if volunteer not found
        """
        result = self.volunteer_data_collection.update_one(
            {
                "name": name,
                "email": email
            },
            {"$set": {"applicant_status": new_status}}
        )
        
        return result.modified_count > 0

    @db_connection
    async def update_sheet_url(self, session_name: str, category: str, sheet_url: str) -> bool:
        """
        Update the sheet URL for a specific session and category.
        
        Args:
            session_name: Name of the session
            category: Category to update (it, sel, or chess)
            sheet_url: New sheet URL to set
            
        Returns:
            bool: True if update was successful, False if session not found
        """
        update_field = f"categories.{category}.sheet_url"
        result = self.sessions_data_collection.update_one(
            {"session_name": session_name},
            {"$set": {update_field: sheet_url}}
        )        
        return result.modified_count > 0

    @db_connection
    async def delete_session_data(self, session_name: str) -> None:
        # Delete the session document
        self.sessions_data_collection.delete_one({"session_name": session_name})
        # Delete all students associated with the session
        self.volunteer_data_collection.delete_many({"session_name": session_name})

    @db_connection
    async def delete_volunteers_by_category(self, session_name: str, category: str) -> None:
        """
        Delete all volunteer data for a specific session and category.
        
        Args:
            session_name: Name of the session
            category: Category of volunteers to delete (it, sel, or chess)
        """
        self.volunteer_data_collection.delete_many({
            "session_name": session_name,
            "category": category
        })

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

