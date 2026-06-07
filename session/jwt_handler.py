from jwt import decode , encode
from functools import wraps
from model.models import userdata , jwt_blacklist
from datetime import datetime , timedelta , timezone


async def wrappper(User : userdata, SECRET_KEY : str,  mins : int| None = 24*60, *args , **kwargs) -> str:
    # for using the UTC globally
    now = datetime.now(timezone.utc)
    # jwt structure
    exp = timedelta(minutes=mins)
    data = {
        "sub": User.user_id,
        "user_name" : User.user_name,
        "iat" : now,
        "exp" : now + exp
    }

    encoded = encode(data,SECRET_KEY, algorithm="HS256")
    return encoded