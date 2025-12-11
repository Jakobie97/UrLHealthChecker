# Import the Flask class from the flask package
from flask import Flask, render_template
from main import myListofUrls

# Create an instance of the Flask class, passing the name of the current module
app = Flask(__name__)

# Use the route() decorator to bind a URL path (e.g., '/') to a function
@app.route('/')
def hello_world():
    return render_template('display_data.html', users=myListofUrls)

# Run the application if the script is executed directly
if __name__ == '__main__':
    # Run the app in debug mode
    app.run(debug=True)
