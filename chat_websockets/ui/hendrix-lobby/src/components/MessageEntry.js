import React from 'react'
import { PropTypes } from 'prop-types'
import './MessageEntry.css'

function timeConverter(UNIX_timestamp) {
    var a = new Date(UNIX_timestamp * 1000)
    var months = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
    ]
    var year = a.getFullYear()
    var month = months[a.getMonth()]
    var date = a.getDate()
    var hour = a.getHours()
    var min = a.getMinutes()
    var sec = a.getSeconds()
    var time = hour + ':' + min + ':' + sec
    var dater = date + ' ' + month + ' ' + year + ' '
    return [dater, time]
}
class MessageEntry extends React.Component {
    renderTxtDiv(content, compWidth) {
        let styleWidth = {
            width: `${compWidth}px`,
            overflowWrap: 'break-word',
        }
        return (
            <div
                className="txt-content"
                style={styleWidth}
                dangerouslySetInnerHTML={{
                    __html: content,
                }}
            ></div>
        )
        //let elem = `<div className="txt-content" style="width:${compWidth}px;overflow-wrap:break-word;">${content}</div>`
        //return elem
    }

    render() {
        const { value } = this.props
        const isHendrix = value.from_nym === 'hendrix'
        const compWidth = isHendrix ? 540 : 540
        const dateTime = timeConverter(value.date_created)
        const date = dateTime[0]
        const time = dateTime[1]
        return (
            <div className="entry-msg">
                <div className="image-frame block-msg">
                    {isHendrix ? (
                        <img
                            src="./hendrix.gif"
                            alt="hendrix"
                            width={68}
                            height={90}
                        ></img>
                    ) : (
                        <img
                            src="./djunxiety.webp"
                            alt="djunxiety"
                            width={68}
                            height={58}
                        ></img>
                    )}
                </div>
                <div className="block-msg msg-header">
                    {!isHendrix ? (
                        <div className="nym-content">{`${value.from_nym}`}</div>
                    ) : null}
                    <div className="date-msg">{date}</div>
                    <div className="date-msg">{time}</div>
                </div>
                <div className="block-msg">
                    <div className="content">
                        {this.renderTxtDiv(value.content, compWidth)}
                    </div>
                </div>
            </div>
        )
    }
}
MessageEntry.propTypes = {
    value: PropTypes.shape({
        content: PropTypes.string.isRequired,
        date_created: PropTypes.number.isRequired,
        from_nym: PropTypes.string.isRequired,
        token: PropTypes.string,
    }),
}
export { MessageEntry }
