import React from 'react'
import { PropTypes } from 'prop-types'
import './MessageEntry.css'
import { isMobileLayout } from '../utils/utils'
import classNames from 'classnames'

export let compWidth
if (isMobileLayout()) {
    compWidth = 260
} else {
    compWidth = 600
}
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
    hour = hour < 10 ? '0' + hour : hour
    var min = a.getMinutes()
    min = min < 10 ? '0' + min : min
    var sec = a.getSeconds()
    sec = sec < 10 ? '0' + sec : sec
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
        const { value, color } = this.props
        const isHendrix = value.from_nym === 'hendrix'

        const dateTime = timeConverter(value.date_created)
        const date = dateTime[0]
        const time = dateTime[1]
        const imageClass = classNames('bg-border-blur')
        const blurredClass = classNames(
            { 'bg-image-blur': !isHendrix },
            'image-frame',
            'block-msg'
        )
        return (
            <div className="entry-msg">
                <div className={blurredClass}>
                    <div className={imageClass}>
                        {isHendrix ? (
                            <img
                                src="./hendrix.gif"
                                alt="hendrix"
                                className="immg"
                                width={68}
                                height={90}
                            ></img>
                        ) : (
                            <img
                                src="./djunxiety.webp"
                                alt="djunxiety"
                                className="immg"
                                width={68}
                                height={58}
                            ></img>
                        )}
                    </div>
                </div>
                <div className="block-msg msg-header">
                    {!isHendrix ? (
                        <div className="nym-content">
                            <font color={color}>{`${value.from_nym}`}</font>
                        </div>
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
    color: PropTypes.string.isRequired,
}
export { MessageEntry }
