import { combineReducers } from 'redux'
import { connectionReducer } from './connection'
import { protoReducer } from './proto'

export const rootReducer = combineReducers({
    connection: connectionReducer,
    proto: protoReducer,
})
