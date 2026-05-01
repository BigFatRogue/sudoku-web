import Table from "./table.js"
import Timer from "./timer.js"
import CustomDropDownList from "./custom_select.js"


const MODE = {
    CLASSIC: 1,
    SOLVING: 2
}

let current_mode = MODE.CLASSIC

const table = new Table()
const timer = new Timer(table)
timer.addEventListener(saveState)

table.createTable()

const customSelectTitle = document.querySelector('.custom-list-title')
const customSelectdropDown = document.querySelector('.dropdown-list')
const customSelecTBody = document.querySelector('.custom-select-table tbody')

const customSelect = new CustomDropDownList(
    customSelectTitle, 
    customSelectdropDown, 
    customSelecTBody
)

customSelect.addEventListenerBeforeSelect((sudoku_id) => {
    saveState()
    customSelect.activeOption.children[2].textContent = timer.htmlClockFace.textContent
    fillTableFromSudokuId(sudoku_id)
})

window.addEventListener('beforeunload', (event) => {
    if (current_mode === MODE.CLASSIC) {
        event.preventDefault()
        timer.stopTimer()
        saveState()
    }
})

document.addEventListener('visibilitychange', () => {
    if (document.hidden && current_mode === MODE.CLASSIC) {
        timer.stopTimer()
        saveState()
    }
})

function fillTableFromSudokuId(sudoku_id) {
    fetch(`api/v1/sudoku/sudoku_user/${sudoku_id}`,
    {
        headers: {'Content-Type': 'application/json'},
        method: "GET"
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            table.clear()
            table.fillSudoku(data.sudoku)
            table.fillSolution(data.solution)
            timer.setTime(data.solving_time)
            timer.startTimer()
        }
    })
}

function setUserName(username) {
    if (username) {
        document.querySelector('#username').style.display = 'block'
        document.querySelector('#username').textContent = `[${username}]`
        document.querySelector('#link-auth').style.display = 'none'
        document.querySelector('#link-logout').style.display = 'block'
    } else {
        document.querySelector('#username').style.display = 'none'
        document.querySelector('#link-auth').style.display = 'block'
        document.querySelector('#link-logout').style.display = 'none'
    }
}

function setUser() {
    fetch('api/v1/auth/user',
        {
            headers: {'Content-Type': 'application/json'},
            method: "POST"
        }
    )
    .then(response => response.json())
    .then(data => {
        setUserName(data.username)
        setUserSolution()
    })
    .catch(e => {console.error(e)})
}

function setUserSolution() {
    fetch('api/v1/sudoku/list_user',
        {
            headers: {'Content-Type': 'application/json'},
            method: "GET"
        }
    )
    .then(response => response.json())
    .then(data => {
        customSelect.fill(data)
        data.forEach(solution => {
            if (solution.is_active) {
                const sudoku_id = solution.sudoku_id
                fetch(`api/v1/sudoku/active_sudoku_user/${sudoku_id}`, 
                    {
                        headers: {'Content-Type': 'application/json'},
                        method: "GET"
                    }
                )
                .then(response => response.json())
                .then(data => {
                    customSelect.setCurrentOptionFromId(sudoku_id)
                    table.fillSudoku(data.sudoku)
                    table.fillSolution(data.solution)
                })
            }
        })
    })
    .catch(e => {console.error(e)})
}

setUser()



function saveState() {
    const sudokuStr = table.toStr()
    const timeSecond = timer.time
    const sudoku_id = customSelect.activeOption.dataset.value
    const isActive = customSelect.activeOption.classList.contains('active')
    const isSolved = customSelect.activeOption.classList.contains('solved')
    fetch('api/v1/sudoku/update_solution',
        {
            headers: {'Content-Type': 'application/json'},
            method: "POST",
            body: JSON.stringify({
                'solution': sudokuStr, 
                'sudoku_id': sudoku_id, 
                'solving_time': timeSecond,
                'is_active': isActive,
                'is_solved': isSolved
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data)
        })

}

const btnChooseMode = document.querySelectorAll('.header-button[data-mode]')
btnChooseMode.forEach(item => {
    item.addEventListener('click', (event) => {
        btnChooseMode.forEach(item => {item.classList.remove('activated')})
        const element = event.target
        const classListElement = element.classList 
        
        if (!classListElement.contains('activated')) {
            classListElement.add('activated')
            activate_mode(Number(element.dataset.mode))
        }
    })
})


function activate_mode(mode) {
    if (mode !== current_mode) {
        switch(mode) {
            case MODE.CLASSIC:
                activeModeClassic(mode)
                break
            case MODE.SOLVING:
                saveState()
                activeModeSolving(mode)
                break
        }
        current_mode = mode
        switchMenu(mode)
    }
}

function activeModeClassic() {
    table.clear()
    fillTableFromSudokuId(customSelect.activeOption.dataset.value)
}

function activeModeSolving() {
    timer.stopTimer()
    table.clear()
    table.hideDigitTable(false)
}

function switchMenu(mode) {
    document.querySelectorAll('.menu[data-mode]').forEach(item => {
        item.classList.remove('is-active')
    })
    document.querySelector(`.menu[data-mode="${mode}"]`).classList.add('is-active')
}

const btnSolving = document.getElementById('btn-solving')
btnSolving.addEventListener('click', () => {
    const sudoku = table.toStr()
    fetch('api/v1/sudoku/solution',
        {
            headers: {'Content-Type': 'application/json'},
            method: 'POST',
            body: JSON.stringify({'sudoku': sudoku, id: null})
        }
    )
    .then(response => response.json())
    .then(data => {
        table.fillSolution(data.solution[0])
    })
})

document.querySelector('#link-logout').addEventListener('click', (event) => {
        fetch('api/v1/auth/logout',
        {
            headers: {'Content-Type': 'application/json'},
            method: 'POST'
        }
    )
    .then(response => response.json())
    .then(data => {
        // switchUserName(undefined)
        location.reload()
    })
})

timer.startTimer()