import React from 'react'
import ReactDOM from 'react-dom'
import App from './components/App'

import { Provider } from 'react-redux'
import { store } from './store/configureStore'
import * as serviceWorker from './serviceWorker'

import './index.css'

ReactDOM.render(
    <Provider store={store}>
        <App />
    </Provider>,
    document.getElementById('root')
)
// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA

//handleVKlogin(console.log, console.log)
//getMorePhotos(0, 200, 2019, console.log, console.log)
serviceWorker.unregister()