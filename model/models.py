from pydantic import BaseModel 
from sqlmodel import SQLModel , Field

class userdata(SQLModel, table=True):
    user_id : str = Field( primary_key= True, nullable= False, unique=True)
    user_name : str = Field(unique= True, nullable= False)
    password : str = Field(nullable=False)

class jwt_blacklist(SQLModel, table=True):
    user_name : str = Field(nullable= False)
    jwt : str = Field(primary_key=True, nullable=False)

class changedata(BaseModel):
    user_name : str 
    old_password : str
    new_password : str
