export default class CustomDropDownList {
    STATE_ENUM = {
        OPEN: 1,
        CLOSE: 0
    }

    constructor(htmlTitle, htmlDropDown, htmTlBody) {
        this.state = this.STATE_ENUM.CLOSE 
        this.htmlTitle = htmlTitle
        this.htmlDropDown = htmlDropDown
        this.htmlTBody = htmTlBody
        this.label = null
        this.options = null
        this.activeOption = null
        this.eventSelect = null

        this.#init()
    }
    
    #init() {
        this.htmlTitle.addEventListener('click', () => {this.#htmlTitleClick()})
        // this.htmlDropDown.addEventListener('', () => {this.#htmlTitleClick()})
    }

    #htmlTitleClick() {
        if (this.state === this.STATE_ENUM.CLOSE) {
            this.htmlDropDown.style.display = 'block'
            this.state = this.STATE_ENUM.OPEN

            const topDropDown = this.htmlDropDown.scrollTop
            const topActiveOption = this.activeOption.getBoundingClientRect().top
            this.htmlDropDown.scrollTop = topDropDown + topActiveOption - 160
        } else {
            this.htmlDropDown.style.display = 'none'
            this.state = this.STATE_ENUM.CLOSE
        }
        
    }

    fill(data) {
        let number = 1
        data.forEach(row => {
            const solvingTime = (row.solving_time === 0) ? '--/--' : this.#formatTime(row.solving_time)
            const clear_row = [
                number,
                row.quality,
                solvingTime
            ]
            this.#createRow(clear_row, row.sudoku_id, row.is_solved, row.is_active)
            number += 1
        });
    }

    #createRow(row, sudoku_id, is_solved, is_active) {
        const tr = document.createElement('tr')
        tr.dataset.value = sudoku_id
        tr.addEventListener('click', () => {this.#chooseOption(tr)})
        
        if (is_solved) tr.classList.add('solved')
        if (is_active) tr.classList.add('active')
        
        row.forEach(value => {
            const td = document.createElement('td')
            td.textContent = value
            tr.appendChild(td)
        })
        this.htmlTBody.appendChild(tr)
    }

    #formatTime(seconds) {
        const hours = Math.floor(seconds / 3600)
        const minutes = Math.floor((seconds % 3600) / 60)
        const secs = seconds % 60
        
        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
        } else {
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
        }
    }

    addEventListenerBeforeSelect(callback) {
        this.eventSelect = callback
    }
    
    #chooseOption(tr) {
        if (this.eventSelect) {
            this.eventSelect(tr.dataset.value)
        }
        
        
        this.activeOption = tr
        this.htmlTBody.querySelector('tr.active')?.classList.remove('active')
        tr.classList.add('active')
        
        this.#htmlTitleClick()


    }

    setCurrentOptionFromId(sudoku_id) {
        const nodeList = this.htmlTBody.querySelectorAll('tr')
        for (const i in nodeList) {
            const item = nodeList[i]
            if (item?.dataset?.value === String(sudoku_id)) {
                item.classList.add('active')
                this.activeOption = item
            }
        }
    }
}