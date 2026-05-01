
export default class Table {
    constructor() {
        this.size = 9
        this.htmlTable = document.getElementById('sudoku-table')
        this.htmlCells = null
        this.sudoku_id = null 
    }

    createTable() {
        for (let row = 0; row < this.size; row++) {
            const tr = document.createElement('tr')
            tr.className = `row-${row}`
            for (let column = 0; column < this.size; column++) {
                const td = document.createElement('td')
                td.className = `cell`
                td.dataset.row = row
                td.dataset.column = column
                tr.appendChild(td)
            }
            this.htmlTable.appendChild(tr)
        }

        this.htmlCells = this.htmlTable.querySelectorAll('.cell[data-row][data-column]')
        this.htmlCells.forEach(cell => {
            const row = cell.dataset.row
            const column = cell.dataset.column

            this.#addMouseEnterCell(cell, row, column)
            this.#addMouseLeaveCell(cell, row, column)
            this.#addMouseClickCell(cell)
            this.#addBeforeInputCell(cell)
            this.#addKeyDownCell(cell)
        })

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                    this.htmlTable.querySelector('.is-choose')?.classList.remove('is-choose')
                }
        })
    }

    #addMouseEnterCell(cell, row, column) {
        cell.addEventListener('mouseleave', (event) => {
            cell.classList.remove('active')


            this.htmlTable.querySelectorAll(`[data-row="${row}"]`).forEach(item => {
                item.classList.remove('active-line')
            })

            this.htmlTable.querySelectorAll(`[data-column="${column}"]`).forEach(item => {
                item.classList.remove('active-line')
            })
        })
    }

    #addMouseLeaveCell(cell, row, column) {
        cell.addEventListener('mouseenter', (event) => {
            cell.classList.add('active')
            
            this.htmlTable.querySelectorAll(`[data-row="${row}"]`).forEach(item => {
                if (item !== cell) item.classList.add('active-line')
            })

            this.htmlTable.querySelectorAll(`[data-column="${column}"]`).forEach(item => {
                if (item !== cell) item.classList.add('active-line')
            })
        })
    }

    #addMouseClickCell(cell) {
        cell.addEventListener('click', (event) => {
            this.htmlTable.querySelector('.is-choose')?.classList.remove('is-choose')
            if (!cell.classList.contains('freezed')) {
                cell.classList.add('is-choose')
            }
        })
    }

    #addBeforeInputCell(cell) {
        cell.addEventListener('beforeinput', (event) => {
            const data = event.data
            
            if (!/^[1-9]$/.test(data)) {
                event.preventDefault()
                return
            }

            const text = cell.textContent
            if (text.length >= 1) {
                cell.textContent = data
                event.preventDefault()
                return
            }
        })
    }

    #addKeyDownCell(cell) {
        cell.addEventListener('keyup', (event) => {
            if (['Delete', 'Backspace'].includes(event.key) && !cell.classList.contains('freezed')) {
                cell.textContent = ''
            }
        })
    }

    fillSolution(solutionStr) {
        for (let row = 0; row < this.size; row++) {
            for (let column = 0; column < this.size; column++) {
                const value = solutionStr[column + row * this.size]
                if (value !== '0') {
                    document.querySelector(`[data-row="${row}"][data-column="${column}"]`).textContent = value
                }
            }
        }
    }

    fillSudoku(sudokuStr) {
        for (let row = 0; row < this.size; row++) {
            for (let column = 0; column < this.size; column++) {
                const td = document.querySelector(`[data-row="${row}"][data-column="${column}"]`)
                const value = sudokuStr[column + row * this.size]
                td.contentEditable = false
                if (value !== '0') {
                    td.textContent = value
                    td.classList.add('freezed')
                }
                else {
                    td.contentEditable = true
                }
            }
        }
    }

    hideDigitTable(hide) {
        this.htmlCells.forEach(htmlCell => {
            htmlCell.style.visibility = (hide) ? 'hidden' : 'visible'
        })
    }

    clear() {
        for (let row = 0; row < this.size; row++) {
            for (let column = 0; column < this.size; column++) {
                const td = document.querySelector(`[data-row="${row}"][data-column="${column}"]`)
                td.textContent = ''
                td.className = 'cell'
                td.contentEditable = true
            }
        }
    }

    toStr() {
        let sudoku = ''

        for (let row = 0; row < this.size; row++) {
            for (let column = 0; column < this.size; column++) {
                const value = document.querySelector(`[data-row="${row}"][data-column="${column}"]`).textContent
                sudoku += (value !== '') ? value : '0'
            }
        }
        console.log(sudoku)
        return sudoku
    }

}






