from fastapi import FastAPI
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import Field
from uuid import uuid4


app=FastAPI( )

# sample requests and queries
@app.get("/")
async def root() :
    return {"message" : "Hello World"}

# sample path paramters => entries in URL
@app.get("/hello/{name}")
async def say_hello(name: str) :
    return {"message" : f"Hello {name}"}

# Path parameters predefined values
# https://fastapi.tiangolo.com/tutorial/path-params/
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/v1/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

# query parametres are added as elements to the url e.g. items?skip=10&limit=3
# https://fastapi.tiangolo.com/tutorial/query-params/
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/v2/items")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

# Optional parameters added to query, one of the element in Union
from typing import Union

#In this case, there are 3 query parameters:
# needy, a required str.
# skip, an int with a default value of 0.
# limit, an optional int.

@app.get("/v3/items/{item_id}")
async def read_user_item(
    item_id: str, needy: str, skip: int = 0, limit: Union[int, None] = None
):
    item = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}
    return item

# if you want to send it as a request body you have to define the class inheritet from pydantic base model
# Request Body
# https://fastapi.tiangolo.com/tutorial/body/
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
# create model
@app.post("/v4/items/")
async def create_item(item: Item):
    return item
# using model

@app.post("/v5/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

# all together

@app.put("/v6/items/{item_id}")
async def create_item(item_id: int, item: Item, q: Union[str, None] = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result

# If the parameter is also declared in the path, it will be used as a path parameter.
# If the parameter is of a singular type (like int, float, str, bool, etc) it will be interpreted as a query parameter.
# If the parameter is declared to be of the type of a Pydantic model, it will be interpreted as a request body.

# additional status code:
# https://fastapi.tiangolo.com/advanced/additional-status-codes/

from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse

items = {"foo": {"name": "Fighters", "size": 6}, "bar": {"name": "Tenders", "size": 3}}

@app.put("/v7/items/{item_id}")
async def upsert_item(
    item_id: str,
    name: Union[str, None] = Body(default=None),
    size: Union[int, None] = Body(default=None),
):
    if item_id in items:
        item = items[item_id]
        item["name"] = name
        item["size"] = size
        return item
    else:
        item = {"name": name, "size": size}
        items[item_id] = item
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)

@app.delete("/v8/items/delete")
async def delete_and_error(error :int):
    return_content = ""
    if error >= 400 and error < 500 :
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=return_content)
    elif error >= 500 and error <600:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=return_content)
    else:
        return JSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED, content=return_content)



#pydantic models
class VoteOption(BaseModel):
    option_id: str
    option_text: str
    votes: int = 0

class PollCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    options: List[str] = Field(..., min_items=2)

class PollUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

class Poll(BaseModel):
    poll_id: str
    title: str
    description: Optional[str]
    options: List[VoteOption]
    created_at: datetime
    total_votes: int = 0

class VoteCast(BaseModel):
    option_id: str

class VoteResponse(BaseModel):
    message: str
    poll_id: str
    option_id: str
    current_votes: int

#storage for polls
polls_db: Dict[str, Poll] = {}

@app.post("/api/polls", response_model=Poll, status_code=status.HTTP_201_CREATED)
async def create_poll(poll_data: PollCreate):
    poll_id = str(uuid4())
    
    options = [
        VoteOption(option_id=str(uuid4()), option_text=opt, votes=0)
        for opt in poll_data.options
    ]
    
    new_poll = Poll(
        poll_id=poll_id,
        title=poll_data.title,
        description=poll_data.description,
        options=options,
        created_at=datetime.utcnow(),
        total_votes=0
    )
    
    polls_db[poll_id] = new_poll
    return new_poll

@app.get("/api/polls", response_model=List[Poll])
async def list_polls():
    return list(polls_db.values())

@app.get("/api/polls/{poll_id}", response_model=Poll)
async def get_poll(poll_id: str):
    if poll_id not in polls_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Poll not found"}
        )
    return polls_db[poll_id]

@app.put("/api/polls/{poll_id}", response_model=Poll)
async def update_poll(poll_id: str, poll_update: PollUpdate):
    if poll_id not in polls_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Poll not found"}
        )
    
    poll = polls_db[poll_id]
    if poll_update.title is not None:
        poll.title = poll_update.title
    if poll_update.description is not None:
        poll.description = poll_update.description
    
    return poll

@app.delete("/api/polls/{poll_id}")
async def delete_poll(poll_id: str):
    if poll_id not in polls_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Poll not found"}
        )
    
    del polls_db[poll_id]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Poll deleted successfully"}
    )

@app.post("/api/polls/{poll_id}/vote", response_model=VoteResponse)
async def cast_vote(poll_id: str, vote: VoteCast):
    if poll_id not in polls_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Poll not found"}
        )
    
    poll = polls_db[poll_id]
    
    option_found = False
    for option in poll.options:
        if option.option_id == vote.option_id:
            option.votes += 1
            poll.total_votes += 1
            option_found = True
            
            return VoteResponse(
                message="Vote cast successfully",
                poll_id=poll_id,
                option_id=vote.option_id,
                current_votes=option.votes
            )
    
    if not option_found:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Option not found in this poll"}
        )

@app.get("/api/polls/{poll_id}/results")
async def get_results(poll_id: str):
    if poll_id not in polls_db:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Poll not found"}
        )
    
    poll = polls_db[poll_id]
    
    results = {
        "poll_id": poll.poll_id,
        "title": poll.title,
        "description": poll.description,
        "total_votes": poll.total_votes,
        "created_at": poll.created_at.isoformat(),
        "options": [
            {
                "option_id": opt.option_id,
                "option_text": opt.option_text,
                "votes": opt.votes,
                "percentage": round((opt.votes / poll.total_votes * 100), 2) if poll.total_votes > 0 else 0
            }
            for opt in poll.options
        ]
    }
    
    return results