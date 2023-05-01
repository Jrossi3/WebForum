# pylint: disable=no-member
from flask import Flask, request, jsonify
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from threading import Lock
import secrets

# Define the connection URL and database name
url = "mongodb://localhost:27017/"
db_name = "web_forum_database"
flag = False

# Create a MongoClient object and access the database
client = MongoClient(url)
db = client[db_name]

# Define a lock object to manage access to global state
lock = Lock()

app = Flask(__name__)


@app.route("/post", methods=["POST"])
def post_request():
    body = request.get_json(force=True)
    msg = body['msg']
    if not isinstance(msg, str) or msg is None:
        return "Post content should be of type string", 400

    # Generate a new UUID for the post
    max_id_doc = db["posts_collection"].find_one(sort=[("id", -1)])
    if max_id_doc is None:
        max_id = 0
    else:
        max_id = max_id_doc["id"]

    # Generate a new post_id by incrementing the maximum post_id
    post_id = max_id + 1

    # Get the current time
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    # Generate a random key
    key = secrets.token_hex(16)

    # Create a new post object with the UUID, message, and timestamp
    new_post = {
        "id": post_id,
        "msg": msg,
        "key": key,
        "timestamp": timestamp,
        "thread": []
    }

    # Insert the new post object into the database
    with lock:
        posts_collection = db["posts_collection"]
        posts_collection.insert_one(new_post)

    inserted_post = posts_collection.find_one({"id": post_id})

    post_dict = dict(inserted_post)
    post_dict.pop("_id", None)
    return jsonify(post_dict), 200


@app.route("/post/<int:id>", methods=["POST"])
def threaded_replies(id):
    body = request.get_json(force=True)
    msg = body['msg']
    if not isinstance(msg, str) or msg is None:
        return "Post content should be of type string", 400
    
    key = secrets.token_hex(16)
    # parent_post = db["posts_collection"].find_one({"id": id})
    # if parent_post is None:
    #     return "Parent post not found", 404
        
    

    # # Generate a new reply id
    # max_reply_id = parent_post.get("max_reply_id", 0)
    # reply_id = max_reply_id + 1
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        # Generate a new UUID for the post
    max_id_doc = db["posts_collection"].find_one(sort=[("id", -1)])
    if max_id_doc is None:
        max_id = 0
    else:
        max_id = max_id_doc["id"]

    # Generate a new post_id by incrementing the maximum post_id
    reply_id = max_id + 1
    

    reply = {
        "id": reply_id,
        "msg": msg,
        "key": key,
        "timestamp": timestamp,
        # "parent_id": parent_post["id"],
        "thread": []
    }
    # Insert the new post object into the database
    with lock:
        posts_collection = db["posts_collection"]
        posts_collection.insert_one(reply)

    with lock:
        posts_collection = db["posts_collection"]
        posts_collection.update_one(
            {"id": id},
            {"$push": {"thread": reply_id}}
        )

    inserted_post = posts_collection.find_one({"id": reply_id})

    post_dict = dict(inserted_post)
    post_dict.pop("_id", None)
    post_dict.pop("key", None)
    post_dict.pop("thread", None)
    return jsonify(post_dict), 200

    # return jsonify(reply), 200

@app.route("/post/<string:start>/<string:end>", methods=['GET'])
def date_time_queries(start, end):
    if start.lower() == "none":
        start = start.lower()
    if end.lower() == "none":
        end = end.lower()
    # print(end)
    with lock:
        posts_collection = db["posts_collection"]
        if start == "none" and end == "none":
            return "Both Start and End cannot be None", 404
        elif start == "none":
            posts = posts_collection.find({"timestamp": {"$lte": end}})
        elif end == "none":
            posts = posts_collection.find({"timestamp": {"$gte": start}})
        else:
            posts = posts_collection.find({"timestamp": {"$gte": start, "$lte": end}})

    result = []
    for post in posts:
        post_dict = dict(post)
        post_dict.pop("_id", None)
        result.append(post_dict)

    return jsonify(result), 200

@app.route("/post/<int:id>", methods=['GET'])
def get_post(id):
    # Get a post from the database by ID
    with lock:
        posts_collection = db["posts_collection"]
        post = posts_collection.find_one({"id": id})

    if post is None:
        return f"Post with ID: {id} not found", 404

    post_dict = dict(post)
    post_dict.pop("_id", None)
    return jsonify(post_dict), 200

@app.route("/post/fulltext/<string:msg>", methods=['GET'])
def get_text(msg):
    # Get all posts from the database
    with lock:
        posts_collection = db["posts_collection"]
        posts_cursor = posts_collection.find()

    # Convert posts from a cursor to a list
    posts_list = []
    for post in posts_cursor:
        post_dict = dict(post)
        post_dict.pop("_id", None)
        if post_dict["msg"] == msg:
            posts_list.append(post_dict)

    return jsonify(posts_list), 200

@app.route("/post/<int:id>/delete/<string:key>", methods=["DELETE"])
def delete_post(id, key):
    # Find the post with the given ID
    with lock:
        posts_collection = db["posts_collection"]
        post = posts_collection.find_one({"id": id})

    # Check if the post exists
    if post is None:
        return f"Post with ID: {id} not found", 404

    # Check if the key matches
    if post["key"] != key:
        return "Forbidden", 403

    # Delete the post
    with lock:
        result = posts_collection.delete_one({"id": id})

    # Check if the deletion was successful
    if result.deleted_count == 0:
        return "Internal Server Error", 500

    post_dict = dict(post)
    post_dict.pop("_id", None)
    return jsonify(post_dict), 200


@app.route("/post/<int:id>/update/<string:key>", methods=["PUT"])
def update_post(id, key):
    global flag
    body = request.get_json(force=True)
    msg = body['msg']
    if not isinstance(msg, str) or msg is None:
        return "Post content should be of type string", 400

    # Find the post with the given ID
    with lock:
        posts_collection = db["posts_collection"]
        post = posts_collection.find_one({"id": id})

    # Check if the post exists
    if post is None:
        return f"Post with ID: {id} not found", 404

    # Check if the key matches
    if post["key"] != key:
        return "Forbidden", 403

    # Check if the new data is the same as the existing stuff
    if post["msg"] == msg:
        flag = True

    # Update the post message
    with lock:
        result = posts_collection.update_one(
            {"id": id}, {"$set": {"msg": msg}})

    # Check if the update was successful
    if result.modified_count == 0 and flag == False:
        return "Internal Server Error", 500

    updated_post = posts_collection.find_one({"id": id})

    post_dict = dict(updated_post)
    post_dict.pop("_id", None)
    if flag == False:
        return jsonify(post_dict), 200
    else:
        flag = False
        return jsonify(post_dict), 201

if __name__ == "__main__":
    app.run()

