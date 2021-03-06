import React from 'react'
import { BrowserRouter, Switch, Link, Route } from 'react-router-dom'
import './styles/style.scss'

import Login from './components/LoginHome'
import BasicSignUp from './components/BasicSignUp'
import Settings from './components/Settings'
import UpdateProfile from './components/UpdateUserProfile'

import Matches from './components/Matches'
import ChatPage from './components/ChatPage'
import Swipe from './components/SwipeView'
import Profile from './components/UserProfile'

const App = () => (
  <BrowserRouter>
    <Switch>
      <Route exact path="/" component={Login} />
      <Route exact path="/signup" component={BasicSignUp} />
      <Route exact path="/settings" component={Settings} />
      <Route exact path="/updateprofile/:userID" component={UpdateProfile} />
      <Route exact path="/matches" component={Matches} />
      <Route exact path="/swipe" component={Swipe} />
      <Route exact path="/matches/chat/:chatID" component={ChatPage} />
      <Route exact path="/profile/:userID" component={Profile} />

    </Switch>
  </BrowserRouter>
)


export default App