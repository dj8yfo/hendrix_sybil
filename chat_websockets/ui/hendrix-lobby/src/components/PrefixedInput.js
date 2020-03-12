import React from 'react'
import './PrefixedInput.css'

const menuSpecial = '/menu'
const rentRoom = '/rent-lavatory-room'

function isString(value) {
    return typeof value === 'string' || value instanceof String
}

class PrefixedInput extends React.Component {
    constructor(props) {
        super(props)
        this.input = React.createRef()
    }
    commonHandler = () => {
        if (!this.input.current.value) return
        let message = this.input.current.value
        this.input.current.value = ''
        if (message.startsWith(menuSpecial)) {
            this.props.query()
        } else if (message.startsWith(rentRoom)) {
            let substr = message.split(' ')
            if (
                substr.length === 2 &&
                isString(substr[1]) &&
                substr[1].length > 0
            ) {
                let nextRoom = substr[1]
                console.log(nextRoom)
                this.props.changeRoom(nextRoom)
            } else {
                return
            }
        } else {
            this.props.sender(message)
        }
    }

    keyPrsHandler = ev => {
        if (ev.keyCode === 13 || ev.which === 13) {
            console.log(ev)
            this.commonHandler()
            return false
        } else {
            return true
        }
    }

    btnClickHandler = ev => {
        ev.preventDefault()
        this.commonHandler()
    }
    render() {
        const { disabled } = this.props
        return (
            <div>
                <button
                    className="btn shifted-btn"
                    onClick={this.btnClickHandler}
                    disabled={disabled}
                >
                    {' '}
                    say
                </button>
                <div className="pref-input-container">
                    <input
                        id="unique_say"
                        className="prefixed-input"
                        type="text"
                        onKeyPress={this.keyPrsHandler}
                        disabled={disabled}
                        ref={this.input}
                    />
                    <span className="inside-prefixed-input">$</span>
                </div>
            </div>
        )
    }
}

export { PrefixedInput }
