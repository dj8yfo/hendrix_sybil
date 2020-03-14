import { combineReducers } from 'redux'
import { connectionReducer } from './connection'
import { protoReducer } from './proto'
import { messagesReducer } from './messages'
import { statusLastMessageReducer } from './lastMessage.js'

export const rootReducer = combineReducers({
    connection: connectionReducer,
    proto: protoReducer,
    messages: messagesReducer,
    statusLast: statusLastMessageReducer,
})
