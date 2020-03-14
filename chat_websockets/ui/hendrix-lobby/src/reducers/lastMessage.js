import { PROTO_GENERIC } from '../actions/proto'
import { CONNECT_TO_WS_CLOSED } from '../actions/connectionActions'

const initialState = {
    info: {},
}
export function statusLastMessageReducer(state = initialState, action) {
    switch (action.type) {
        case PROTO_GENERIC:
            return {
                ...state,
                info: action.payload,
            }
        case CONNECT_TO_WS_CLOSED:
            return {
                ...state,
                info: {},
            }
        default:
            return state
    }
}
