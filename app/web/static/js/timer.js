export default class Timer {
    STATUS_TIMER = {
        PLAY: 1,
        PAUSE: 0
    }
    constructor(table) {
        this.status = this.STATUS_TIMER.PAUSE
        this.table = table
        this.intervalId = null
        this.time = 0
        this.timeDelay = 1000
        this.htmlBtnTimer = document.getElementById('btn-timer')
        this.htmlClockFace = document.getElementById('clock-face')
        this.eventPouse = null

        this.initEventListeners()
    }

    initEventListeners() {
        this.htmlBtnTimer.addEventListener('click', () => {
            if (this.status === this.STATUS_TIMER.PAUSE) {
                this.startTimer()
                
            } else {
                this.stopTimer()
                
            }
        })
    }

    startTimer() {
        if (this.status === this.STATUS_TIMER.PLAY) return

        this.status = this.STATUS_TIMER.PLAY
        this.updateButtonText()

        this.intervalId = setInterval(() => {
            this.time++
            this.updateDisplay()
        }, this.timeDelay)

        this.table.hideDigitTable(false)
        this.htmlBtnTimer.style.backgroundImage = "url('../web/static/image/pause.png')"
    }

    stopTimer() {
        if (this.status === this.STATUS_TIMER.PAUSE) return
        
        this.status = this.STATUS_TIMER.PAUSE
        
        if (this.intervalId) {
            clearInterval(this.intervalId)
            this.intervalId = null
        }
        
        this.updateButtonText()
        this.table.hideDigitTable(true)
        this.htmlBtnTimer.style.backgroundImage = "url('../web/static/image/play.png')"

        if (this.eventPouse) this.eventPouse()
    }

    updateDisplay() {
        if (this.htmlClockFace) {
            this.htmlClockFace.textContent = this.formatTime(this.time)
        }
    }
    
    updateButtonText() {
        if (this.htmlClockFace) {
            this.htmlClockFace.textContent = this.formatTime(this.time)
        }
    }

    setTime(second) {
        this.time = second
        this.updateDisplay()
    }

    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600)
        const minutes = Math.floor((seconds % 3600) / 60)
        const secs = seconds % 60
        
        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
        } else {
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
        }
    }

    clear() {
        this.destroy()
        this.time = 0
        this.status = this.STATUS_TIMER.PAUSE
        this.updateDisplay()
    }

    destroy() {
        if (this.intervalId) {
            clearInterval(this.intervalId)
            this.intervalId = null
        }
    }

    addEventListener(func) {
        this.eventPouse = func
    }
}