#!/bin/bash
# echo "├─ pymongo"
# pip3 install pymongo
# echo "├─ secrets"
# pip3 install secrets

# Start the app in the background
python3 app.py &
PID=$!

# Wait for the app to start up
sleep 2

# Function to clear the db

# Test POST /post and GET /post/id
# This test will exit immediately if the POST /post or GET /post/id fails.
curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'
RESPONSE=$(curl http://localhost:5000/post/1)
key=$(echo $RESPONSE | jq -r '.key')
timestamp=$(echo $RESPONSE | jq -r '.timestamp')
id=$(echo $RESPONSE | jq -r '.id')

# GET /post/id test
if [ "$RESPONSE" == "Post with ID: 1 not found" ]; then
  echo "Get /post/id failed."
  exit 1
else
  echo "Get /post/id passed."
fi

# Check if the response matches the expected output
# POST /post test
EXPECTED={'"id"':$id,'"key"':'"'$key'"','"msg"':'"hi my name is jason"','"thread"':[],'"timestamp"':'"'$timestamp'"'}
if [[ "$RESPONSE" != *"$EXPECTED"* ]]; then
  echo "ERROR: POST /post failed"
  echo "Expected: $EXPECTED"
  echo "Actual:   $RESPONSE"
  exit 1
else
  echo "POST /post passed"
fi

# Stop the server
echo "Stopping Flask server..."
kill $PID

# Start the server again
echo "Starting Flask server again..."
flask run &
PID=$!

# Wait for the app to start up
sleep 2

# Testing persistence to see if the post still exists after restarting the server
# This test will exit immediately if the persistence fails.
EXISTS=$(curl http://localhost:5000/post/$id)

if [ "$EXISTS" != "Post with ID: $id not found" ]; then
  echo "Persistence passed."
else
  echo "Persistence failed."
  exit 1
fi

# Testing persistence for a bad request to see if the post still exists
# This test will exit immediately if the persistence fails.
curl http://127.0.0.1:5000/post/fulltext
EXISTS=$(curl http://localhost:5000/post/$id)

if [ "$EXISTS" != "Post with ID: $id not found" ]; then
  echo "Persistence passed."
else
  echo "Persistence failed."
  exit 1
fi

# Testing the delete function by creating 4 more posts and then deleting all 5 of the posts
# This test will exit immediately if the deletion fails. 
counter=2
while [ $counter -le 5 ]
do
  curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'
  ((counter++))
done

counter=1
while [ $counter -le 5 ]
do
  RESPONSE=$(curl http://localhost:5000/post/$counter)
  key=$(echo $RESPONSE | jq -r '.key')
  curl -X DELETE http://127.0.0.1:5000/post/$counter/delete/$key
  EXISTS=$(curl http://localhost:5000/post/$counter)
  if [ "$EXISTS" = "Post with ID: $counter not found" ]; then
    echo "Delete passed."
  else
    echo "Delete failed."
    exit 1
  fi
  ((counter++))
done

# Test the update function
# This should return "Message updated." Otherwise, the test will exit immediately.

curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'
RESPONSE=$(curl http://localhost:5000/post/1)
key=$(echo $RESPONSE | jq -r '.key')
id=$(echo $RESPONSE | jq -r '.id')
msg=$(echo $RESPONSE | jq -r '.msg')
curl -X PUT -d '{"msg": "hello I am update"}' http://127.0.0.1:5000/post/$id/update/$key
New=$(curl http://localhost:5000/post/1)
newMsg=$(echo $New | jq -r '.msg')

if [ "$msg" == "$newMsg" ]; then
  echo "Message update failed."
  exit 1
else
  echo "Message update passed."
fi

# Clean up
key=$(echo $New | jq -r '.key')
curl -X DELETE http://127.0.0.1:5000/post/$id/delete/$key

# Running the same test as before except commenting out the update function to show that the update will not happen
# This is to show that the update function is actually updating the message
# This should return "Message not updated." Otherwise, the test will exit immediately.

curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'
RESPONSE=$(curl http://localhost:5000/post/1)
key=$(echo $RESPONSE | jq -r '.key')
id=$(echo $RESPONSE | jq -r '.id')
msg=$(echo $RESPONSE | jq -r '.msg')
# curl -X PUT -d '{"msg": "hello I am update"}' http://127.0.0.1:5000/post/$id/update/$key
New=$(curl http://localhost:5000/post/1)
newMsg=$(echo $New | jq -r '.msg')

if [ "$msg" != "$newMsg" ]; then
  echo "Message updated."
  exit 1
else
  echo "Message not updated."
fi

# Clean up
key=$(echo $New | jq -r '.key')
curl -X DELETE http://127.0.0.1:5000/post/$id/delete/$key

# Write tests for Fulltext search
# This will exit immediately if the fulltext search fails
curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'
RESPONSE=$(curl http://127.0.0.1:5000/post/fulltext/"hi%20my%20name%20is%20jason")
echo "$RESPONSE"
key=$(echo $RESPONSE | jq -r '.[0].key')
timestamp=$(echo $RESPONSE | jq -r '.[0].timestamp')
id=$(echo $RESPONSE | jq -r '.[0].id')
thread=$(echo $RESPONSE | jq -r '.[0].thread')
msg=$(echo $RESPONSE | jq -r '.[0].msg')
EXPECTED=[{'"id"':$id,'"key"':'"'$key'"','"msg"':'"'$msg'"','"thread"':$thread,'"timestamp"':'"'$timestamp'"'}]
echo "$EXPECTED"

if [ "$RESPONSE" == "$EXPECTED" ]; then
  echo "Fulltext search passed."
else
  echo "Fulltext search failed."
  exit 1
fi

# Clean up
New=$(curl http://localhost:5000/post/1)
id=$(echo $New | jq -r '.id')
key=$(echo $New | jq -r '.key')
curl -X DELETE http://127.0.0.1:5000/post/$id/delete/$key

echo "Yay, all of the tests passed!"

kill $PID
