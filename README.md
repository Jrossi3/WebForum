## Team Members
- Jason Rossi (jrossi3@stevens.edu)
- Nouman Syed (nsyed1@stevens.edu)
- Atishay Jain (ajain70@stevens.edu)

## GitHub Repo Link:
https://github.com/Jrossi3/WebForum

## Time Spent
Each of the group members spent around 20 hours on the project

## Description of how you tested your code
The way we tested our code was through a `test.sh` script. In this file, we would run shell commands to run multiple tests covering various edge-cases for each of the routes we had put together. 

## Any bugs or issues you could not resolve
To the best of our knowledge, there are no known bugs or issues in our endpoints, extensions or scripts.

## An example of a difficult issue or bug and how you resolved
An example of a difficult issue or bug was extracting a key from the shell command and putting it into another shell command. 

## Extensions
1. Update function
   
- This is the route used for the update a post. It works by sending a PATCH request to the following route. `/post/<int:id>/update/<string:key>`
- While updating a post, the user is expected to send as the request body, a JSON Object with a single key, `"msg"` with the value as whatever the content of the updated post needs to be.
- As seen from the route, it also requires and `id` of the post that needs to be updated. And the secret `key` so not everybody can update your posts. This requests responds with the updated post.
- This route also updates the `timestamp` on the post.

2. Fulltext search
- This is the route used for the fulltext search feature. This works when a GET request is sent to the following route: `"/post/fulltext/<string:msg>"`. This extension works by iterating through all the posts that exist and looking for posts with a match with the input string from the query. 
- For example, If I had to look for posts which have their `"msg"` fields as `"Hi my name is Jason"`, I would send a request like `/post/fulltext/"hi%20my%20name%20is%20jason"`. This will find all the posts with matching `"msg"` fields.

3. Persistence
- We used MongoDB to implement persistence of data. This makes sure even if the server restarts, the data is not lost as it is all stored in the Database. This extension does everything as specified in the Spec Sheet. 

4. Data and Time based queries
- This extension works when the user sends a GET request on the `/post/<string:start>/<string:end>` route.
- As seen, there are two query parameters that can either be two valid dates in the ISO 8601 format in UTC or "none"
- `/post/2023-04-30T19:29:03Z/2023-04-30T11:54:23Z` gets all the posts with timestamps between the start and end time given.
- `/post/2023-04-30T19:29:03Z/none` gets all the posts that were made or last updated after the given timestamp. 
- `/post/none/2023-04-30T19:29:03Z` gets all the posts that were made or last updated before the given timestamp.
- `/post/none/none` throws an error telling the user that both start, and end can not be "none"

5. Threaded Replies 
- This extension works when a POST request is sent to the `/post/<int:id>` route. Threaded replies works exactly like Endpoint 1 (Create posts). Except, when a reply post is created, the `id` of the parent post is provided in the query. This `id` is used to fetch the parent post, and insert the `id` of the newly created reply post into the `thread: []` array field present in each post.
- So, to summarize, each post will have the `id`s of all its replies in its `thread` field.

## Detailed Summaries of Tests

1) Update Post

We tested the update message post feature in a very straightforward way. We ran the command `"curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'"` to add a new post. After this, we set `RESPONSE` equal to the new post. We then got the `key`, `msg`, and `id` of the new post and ran the update command: `"curl -X PUT -d '{"msg": "hello I am update"}' http://127.0.0.1:5000/post/$id/update/$key"`. This changed the message from `"hi my name is jason"` to `"hello I am update"`. We then got the updated post and set it equal to New. Then we got the updated message and set it equal to `newMsg`. From here, we checked if `msg` and `newMsg` were equivalent to each other. If they were equal, then the update function has failed to update the message. If they are not equal, then the message was updated. 

2) Fulltext Search

We tested persistence in a very simple way. We ran the command `"curl http://127.0.0.1:5000/post -X POST -d '{"msg": "hi my name is jason"}'"` to add a new post. We then ran the command `'curl http://127.0.0.1:5000/post/fulltext/"hi%20my%20name%20is%20jason"'` to find all matching posts with the message `"hi my name is jason"` essentially targeting the post we just created. This command was set equal to `RESPONSE`. We then created an `EXPECTED` variable, which was then set to the new post that was just created, but the way it was put together was by extracting the information from the new post that was just created and then adding it to a `EXPECTED` variable. Then we checked if the `EXPECTED` was equivalent to the `RESPONSE` and if they were, then the test passed since the search found the new post with the matching message.

3) Persistence

We tested persistence through 2 different ways. Our first way was restarting the server through running two commands to end and start the server. There is a `"kill $PID"` command and a `"flask run &"` command to end and start the server resepctively. The second way of testing was giving it a bad request. The exact command is `"curl http://127.0.0.1:5000/post/fulltext"` and here this is a bad request because it is an unfinished request and therefore will return an error. Then there is a test to see if the post is still existing after the command is run. There are many comments in the testing to show the exact specifics of when these tests occur. 
