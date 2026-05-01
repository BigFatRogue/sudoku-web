const divReg = document.getElementById("registration")
const divAuth = document.getElementById("authentication")
const tabRight = document.getElementById('tab-right')
const tabLeft = document.getElementById('tab-left')
const formAuth = document.getElementById('form-auth')
const formReg = document.getElementById('form-registration')
const msgInfo = document.getElementById('msg-info')

const page = 'auth'


if (page === 'reg') {
    divReg.style.display = "block";
    divAuth.style.display = "none";
    tabRight.className += ' active'
}
else {
    divAuth.style.display = "block";
    divReg.style.display = "none";
    tabLeft.className += ' active'
}


tabRight.addEventListener('click', (event) => {
    open_tab(event, 'registration')
})

tabLeft.addEventListener('click', (event) => {
    open_tab(event, 'authentication')
})

function open_tab(event, log) {
    let tabcontent = document.getElementsByClassName("tab-content")
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    const tablinks = document.querySelectorAll(".tab-links");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "")
    }

    document.getElementById(log).style.display = "block";
    event.currentTarget.className += " active";
}


async function customSubmitForm(
    element, 
    url, 
    message_error,
) {
    try {
        const formData = new FormData(element);
        const response = await fetch(
            url, 
            {
                method: 'POST',
                body: formData
            }
        )

        if (!response.ok) {
            showError(message_error[response.status], response.status)
            await response.json();
        } else {
            showError('Успешный вход', 200)
            await response.json();
            setTimeout(() => {
                window.location.href = '/'
            }, 1000)
        }

        
        
    } catch (error) {
        console.error(error)
        showError('Ошибка соединения', 500)
    }
} 

formAuth.addEventListener('submit', async (event) => {
    event.preventDefault()
    customSubmitForm(
        event.target,
        event.target.action,
        {
            400: 'Неверный пароль',
            404: 'Пользователь не найден',
            401: 'Неверный пароль',
            422: 'Пароль должен быть не менее 8 символов'
        }
    )
})

formReg.addEventListener('submit', async (event) => {
    event.preventDefault()

    customSubmitForm(
        event.target,
        event.target.action,
        {
            400: 'Пароли должны совпадать',
            409: 'Пользователь уже существует',
            422: 'Пароль должен быть не менее 8 символов'

        }
    )
})

function showError(message, status) {
    if (status >= 200 && status < 300) {
        msgInfo.classList.remove('error')
        msgInfo.classList.add('succses')
    } else {
        msgInfo.classList.remove('succses')
        msgInfo.classList.add('error')
    }
    msgInfo.textContent = message;
    msgInfo.style.display = 'flex';
    setTimeout(() => {
        msgInfo.style.display = 'none';
    }, 5000)
} 

//  asdas@adsa.ru