export function clearToken(state, recvdToken) {
    if (recvdToken === state.pendingMsgToken) {
        return ''
    } else {
        return state.pendingMsgToken
    }
}

export function isMobileLayout() {
    if (
        /Mobile|Android|webOS|iPhone|iPad|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera Mini/i.test(
            navigator.userAgent
        )
    ) {
        return true
    } else {
        return false
    }
}

export function getRandomColor() {
    var letters = '0123456789ABCDEF'
    var color = '#'
    for (var i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)]
    }
    return color
}

export function prevMessages(lastMessage) {
    if (lastMessage == null) {
        return 0
    }
    let prevMessage = lastMessage > -1 ? lastMessage + 1 : null
    return prevMessage > 0 ? prevMessage : 0
}
