# Spoondr

## The Overview
This was the fourth and final project of the General Assembly Course. We were set in a group of 3 people, luckily we all had our individual interests that lined up perfectly.

This project was all about using a Python and Flask backend, something none of us had ever done before. Like our third project, we had to create our backend and API and use an external one if needed, We chose not to use any external API's. The frontend was built with ReactJS and Sass.


### What is Spoondr?
Spoondr is a dating app, similar to Tinder, but instead of looking for people to date, you are looking for people to spoon with. You can create and edit your profile, state which gender you are searching for (or you can swipe through all genders) and chat with your matches.

__Technologies Used__

* Python
* Flask
* Websockets (JS frontend - Python Backend)
* PostgreSQL
* ReactJS
* Sass
* Heroku (for deployment)
* Git & GitHub

## The Project 

We all decided to distribute tasks based on each of our interests. 

One of the key issues we were keen to avoid was each of the pages having different styling and generally feeling disconnected. To combat this one of the team members solely focused on the styling and css of the site. 

My other teammate and I took on the backend and front-end functionality of the site. 

I focused mainly on matches and chat functionality. 

##The Plan
For the plan of this project, we needed to consider the different routes we would need on the backend. We used Google Jamboard to all collectively whiteboard the project. 


## The backend  
Utilizing Python, Flask and PostgreSQL for this project provided a lot of new challenges and victories. 

Planning the routes ahead of time benefited us when it came to tackling this part of the project. 

We started from the ground up with the user then working into the more complex relationships such as matches and chat. The chat was powered by WebSockets. 

### Models

Our user model looked like this: 

```python
class User(db.Model, BaseModel):
  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(50), nullable=False, unique=True)
  email = db.Column(db.String(128), nullable=False, unique=True)
  bio = db.Column(db.String(128), nullable=True)
  password_hash = db.Column(db.String(128), nullable=True)
  location = db.Column(db.String(30), nullable=False)
  age = db.Column(db.Integer, nullable=False)
  gender = db.Column(db.String(10), nullable=False)
  gender_preference = db.Column(db.String(10), nullable=False)
  interests = db.relationship('Interests', secondary=user_interests_join, backref='users')
  socials = db.relationship('Socials', secondary=user_socials_join, backref='users')
  images = db.relationship('Images', secondary=user_images_join, backref='users')
  matches = db.relationship('Matches', secondary=user_matches_join, backref='users')
  chats = db.relationship('Chats', secondary=user_chats_join, backref='users')
  

  @hybrid_property
  def password(self):
    pass

  @password.setter
  def password(self, password_plaintext):
    self.password_hash = bcrypt.generate_password_hash(password_plaintext).decode('utf-8')

  def validate_password(self, password_plaintext):
    return bcrypt.check_password_hash(self.password_hash, password_plaintext)

  def generate_token(self):
    payload = { 
      'exp': datetime.utcnow() + timedelta(days=1),
      'iat': datetime.utcnow(),
      'sub': self.id
    }
    token = jwt.encode(payload, secret, 'HS256').decode('utf-8')

    return token
```
As you can see we have used quite a few referenced relationships and also we utilized a confirm password function. 

I have put our interests model and join table below to demonstrate how these relationships work.

Model

```python
class Interests(db.Model, BaseModel):

  __tablename__ = 'interests'

  name = db.Column(db.String(40), unique=True, nullable=True)
```

Join table


```python

user_interests_join = db.Table('user_interests',
  db.Column('interest_id', db.Integer, db.ForeignKey('interests.id'), primary_key=True),
  db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)
```

### Controllers

To keep everything structured and easy to navigate, we created a controller for each of our models. For our user model, we created a controller to handle actions such as signup 

To make our lives easier I wanted to create all a uniform id across all models that connected to our user model. 


```python
@router.route('/signup', methods=['POST'])
def signup():
  user = user_schema.load(request.get_json())
  template_images = Images(
    image1='https://res.cloudinary.com/spoondr/image/upload/v1607006914/Portrait_Placeholder_zu9uoa.png'
  )
  template_social= Socials(
    Instagram ='https://www.instagram.com'
  )
  user.images = [template_images]
  user.socials = [template_social]
  user.save()

  template_match = Matches(
    Liked=[user.id],
    LikedBy=[],
    Matched=[],
    Disliked=[]
  )
  user.matches.append(template_match)
  user.save()
  return user_schema.jsonify(user), 200
```

As you can see from the above I am passing template values in for each of the subsequent models such as images and socials. 

### Challenges

One of the biggest challenges we faced while building the backend was creating the matches model. 

We wanted to be able to append user id's into various matches rows to keep a track of who had liked who and if there were any matches. 

We found that although we could get the append to console log it wasn't saving to the database. 

After a lot of research, I was able to find that the initial arrays were immutable. 

To rectify this we created a block of code that allowed us to mutate the arrays. I have put the finished code below: 

```python
class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()
    
    def remove(self, value):
      list.remove(self, value)
      self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

class Matches(db.Model, BaseModel):

  __tablename__ = 'matches'

  id = db.Column(db.Integer, primary_key=True)
  Liked = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)
  LikedBy = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)
  Matched = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)
  Disliked = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)), nullable=True)


```

As you can see the above is quite different from the user model previously shown. 

## Frontend

My key areas of responsibility on the frontend were the chat page, swipe page and matches. 

### Chat page

On the front end, the chat page was the most complex and time-consuming area of work. 

There were two major challenged with the chat page. The first one was creating a real-time chat between two users. The second was allowing that chat to be persistent so that if a user came back after leaving the site they would see any messages they had missed. 

To solve the first issue we used Websockets.io. 

```javascript
   socket = io('https://project-4-lee.herokuapp.com/', { secure: true })
    socket.connect()
    socket.on('connect', () => {
      socket.emit('join_room', {
        username: `${currentUser.first_name}`,
        room: `${props.match.params.chatID}`
      })
      console.log('connected!')
      updateConnect(true)
    })

```

When the user first joins the room the useEffect fires which connects them to a chatroom which has the id based on their chatID relationship in the database. This allowed me to keep track of which two users should be able to chat with each other. 

The backend handled the bulk of work dealing with WebSockets and handling the historic data. 

```python

@sio.on('send_message')
def handleMessage(data):
  print(data)
  sio.emit('receive_message', data, room=data['room'])
  return None 

@sio.on('join_room')
def handle_join_room(data):
  join_room(data['room'])
  sio.emit(data, room=data['room'])

@router.route('/chat/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
  chat_record = Chats.query.get(chat_id)

  print(chat_record.chat_history)

  return chats_schema.jsonify(chat_record)

@router.route('/chat/<int:chat_id>', methods=['PUT'])
def update_chat(chat_id):
  exsisting_chat = Chats.query.get(chat_id)

  try:
    chat = chats_schema.load(
      request.get_json(),
      instance=exsisting_chat,
      partial=True
    )
  
  except ValidationError as e:
    return {'errors': e.messages, 'message': 'Something went wrong'}
  
  chat.save()

  return chats_schema.jsonify(chat)

 

```

As you can see from the GET and PUT routes we also employed a sort of longpolling to track and store historic messages which solved our second issue. 

### Challenges 

The main challenged faced from this area of the project was due to using python. This means that we couldn't utilize as a single version of WebSockets but had to split the frontend and backend into two different versions. 

For the backend I used flask_socketio and for the frontend I used socket_client. The challenge comes from the version needed for these two to be compatible. Unfortunately just typing into google bared no results and as such, I had to try an alternative route. I managed to find a project on GitHub that was set up similarly, I then checked the version used in the package.json. Replicating in our project solved the issue. 