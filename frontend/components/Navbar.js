import React from 'react'
import { Link, withRouter } from 'react-router-dom'
import SmallLogo from '../images/pear.png'
import { getUserId } from '../lib/UserToken'

const Navbar = () => {
  const currUser = getUserId()

  return <footer>
    <nav>
      <Link to={'/matches'}>
        <img src='https://www.flaticon.com/svg/static/icons/svg/25/25379.svg' alt='link to messages'/>
      </Link>
      <Link to={'/swipe'}>
        <img className="smallLogo" src={SmallLogo} alt='speech bubble'/>
      </Link>
      <Link to={`/updateprofile/${currUser}`}>
        <img src='https://www.flaticon.com/svg/static/icons/svg/2522/2522086.svg' alt='link to own profile'/>
      </Link>
    </nav>
  </footer>

}

export default withRouter(Navbar)