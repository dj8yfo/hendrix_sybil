import React from 'react'
import { connect } from 'react-redux'
import './messages.css'

class Messages extends React.Component {
    renderTemplate(messages) {
        var res = messages.map((value, index) => {
            return (
                <div id={value.date_created} className="entry-msg">
                    <div className="image-frame block-msg">
                        {value.from_nym === 'hendrix' ? (
                            <img
                                src="./hendrix.gif"
                                alt="hendrix"
                                width={45}
                                height={60}
                            ></img>
                        ) : (
                            <img
                                src="./djunxiety.webp"
                                alt="djunxiety"
                                width={70}
                                height={60}
                            ></img>
                        )}
                    </div>
                    <div className="block-msg">
                        {' '}
                        {value.from_nym === 'hendrix'
                            ? null
                            : value.from_nym}{' '}
                    </div>
                    <div className="block-msg">
                        {' '}
                        <div className="content">{value.content}</div>{' '}
                    </div>
                </div>
            )
        })
        return res
    }
    render() {
        console.log('<Messages/ >')
        const { messages } = this.props.messages
        return (
            <div className="msgs">
                <p> Messages </p>
                {this.renderTemplate(messages)}
            </div>
        )
    }
}

const mapStateToProps = store => {
    return {
        messages: store.messages,
    }
}

export default connect(mapStateToProps)(Messages)
