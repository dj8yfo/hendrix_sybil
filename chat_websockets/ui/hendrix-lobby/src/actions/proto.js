export const PROTO_AUTH_STARTED = 'PROTO_AUTH_STARTED'
export function init_authenticate(type, callback, connection) {
    return ev => {
        callback({
            type: type,
            payload: ev,
        })
        const authmessage = {
            action: 'authenticate',
        }
        connection.send(JSON.stringify(authmessage))
        callback({
            type: PROTO_AUTH_STARTED,
            payload: authmessage,
        })
    }
}
