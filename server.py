from sanic import Sanic, text, Request
# Sanic is same as Express, text is same as res.send() and Requests is for dealing with HTTP requests
# We use Sanic to provide a simpler way of getting the highly performant HTTP server up and running that is easy to build,expand and most importantly to scale.

app = Sanic(__name__) 
# Same as const app = express() for JS 
# and __name__ is a special variable used to tell Sanic that this app corresponds to current Python script


# This is a post request handler for the route '/' i.e. the root route
@app.post("/")
async def handler(request: Request):
    message = (
        request.head + b"\n\n" + request.body
    ).decode("utf-8")
    print(message)
    return text("Done")


# When we set name as main ,it means that this script is being run directly and not being imported as a module. The difference is that the code inside the block will only be executed if it is run and not when its imported as a module 
if __name__ == '__main__':
    app.run(port = 9999,debug = True)

