const API_BASE_URL = 'http://localhost:8000';
let accessToken = null;
let currentUsername = null;

// --- UI 요소 선택 ---
const authSection = document.getElementById('auth-section');
const chatSection = document.getElementById('chat-section');

const showLoginButton = document.getElementById('show-login');
const showRegisterButton = document.getElementById('show-register');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

const loginUsernameInput = document.getElementById('loginUsername');
const loginPasswordInput = document.getElementById('loginPassword');
const loginButton = document.getElementById('loginButton');
const loginStatus = document.getElementById('loginStatus');

const registerUsernameInput = document.getElementById('registerUsername');
const registerPasswordInput = document.getElementById('registerPassword');
const registerPasswordConfirmInput = document.getElementById('registerPasswordConfirm');
const registerButton = document.getElementById('registerButton');
const registerStatus = document.getElementById('registerStatus');

const loggedInUser = document.getElementById('loggedInUser');
const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const logoutButton = document.getElementById('logoutButton');
const chatStatus = document.getElementById('chatStatus');

// --- 탭 전환 기능 ---
function showAuthForm(formId) {
    document.querySelectorAll('.form-section').forEach(form => {
        form.classList.remove('active');
    });
    document.getElementById(formId).classList.add('active');

    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    if (formId === 'login-form') {
        showLoginButton.classList.add('active');
    } else {
        showRegisterButton.classList.add('active');
    }
    loginStatus.textContent = '';
    registerStatus.textContent = '';
}

// 탭 버튼 클릭 이벤트 리스너
showLoginButton.addEventListener('click', () => showAuthForm('login-form'));
showRegisterButton.addEventListener('click', () => showAuthForm('register-form'));


// --- 메시지를 채팅창에 추가하는 함수 ---
function addMessage(sender, message, type) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', type);
    msgDiv.textContent = `${sender}: ${message}`;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// --- 채팅 UI (입력 필드/버튼) 활성화/비활성화 함수 ---
function setChatUIEnabled(enabled) {
    chatInput.disabled = !enabled;
    sendButton.disabled = !enabled;
    if (enabled) {
        sendButton.textContent = '전송';
        chatStatus.textContent = '';
    } else {
        sendButton.textContent = '전송 중...';
        chatStatus.textContent = 'AI 응답 대기 중...';
    }
}

// --- 로그인 처리 ---
loginButton.addEventListener('click', async () => {
    const username = loginUsernameInput.value.trim();
    const password = loginPasswordInput.value;
    loginStatus.textContent = '';

    if (!username || !password) {
        loginStatus.textContent = '사용자 이름과 비밀번호를 입력해주세요.';
        return;
    }

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '로그인 실패');
        }

        const data = await response.json();
        accessToken = data.access_token;
        currentUsername = username;
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('username', currentUsername);

        loggedInUser.textContent = currentUsername;
        authSection.style.display = 'none';
        chatSection.style.display = 'block';
        addMessage('System', '로그인 성공! 채팅 기록을 불러오는 중...', 'system-message');
        await loadChatHistory();

    } catch (error) {
        loginStatus.textContent = `로그인 오류: ${error.message}`;
        console.error('로그인 에러:', error);
    }
});

// --- 회원가입 처리 ---
registerButton.addEventListener('click', async () => {
    const username = registerUsernameInput.value.trim();
    const password = registerPasswordInput.value;
    const passwordConfirm = registerPasswordConfirmInput.value;
    registerStatus.textContent = '';

    if (!username || !password || !passwordConfirm) {
        registerStatus.textContent = '사용자 이름과 비밀번호를 입력해주세요.';
        return;
    }
    if (password !== passwordConfirm) {
        registerStatus.textContent = '비밀번호가 일치하지 않습니다.';
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '회원가입 실패');
        }

        const data = await response.json();
        registerStatus.style.color = 'green';
        registerStatus.textContent = `회원가입 성공: ${data.username}님 환영합니다! 이제 로그인해주세요.`;
        registerUsernameInput.value = '';
        registerPasswordInput.value = '';
        registerPasswordConfirmInput.value = '';
        showAuthForm('login-form');

    } catch (error) {
        registerStatus.style.color = 'red';
        registerStatus.textContent = `회원가입 오류: ${error.message}`;
        console.error('회원가입 에러:', error);
    }
});

// --- 채팅 메시지 저장 함수 (프론트엔드에서는 직접 호출되지 않음) ---
async function saveChatMessage(role, content) {
    if (!accessToken || !currentUsername) {
        console.warn("로그인되지 않아 채팅 메시지를 저장할 수 없습니다.");
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/chat/save`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                username: currentUsername,
                role: role,
                content: content,
                timestamp: new Date().toISOString()
            })
        });
        if (!response.ok) {
            const errorData = await response.json();
            console.error('채팅 기록 저장 실패:', errorData.detail || '알 수 없는 오류');
        }
    } catch (error) {
        console.error('채팅 기록 저장 중 네트워크 오류:', error);
    }
}

// --- 채팅 기록 불러오기 함수 ---
async function loadChatHistory() {
    chatWindow.innerHTML = '';
    if (!accessToken || !currentUsername) {
        addMessage('System', '채팅 기록을 불러올 수 없습니다. 로그인해주세요.', 'system-message');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/chat/history`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('인증 실패. 다시 로그인해주세요.');
            }
            const errorData = await response.json();
            throw new Error(errorData.detail || '채팅 기록 불러오기 실패');
        }

        const data = await response.json();
        if (data.history && data.history.length > 0) {
            addMessage('System', '이전 채팅 기록을 불러왔습니다.', 'system-message');
            data.history.forEach(msg => {
                const sender = msg.role === 'user' ? 'You' : 'AI';
                const type = msg.role === 'user' ? 'user-message' : 'ai-message';
                addMessage(sender, msg.content, type);
            });
        } else {
            addMessage('System', '이전 채팅 기록이 없습니다. 새로운 대화를 시작하세요!', 'system-message');
        }

    } catch (error) {
        chatStatus.textContent = `채팅 기록 불러오기 오류: ${error.message}`;
        console.error('채팅 기록 불러오기 에러:', error);
        if (error.message.includes('인증 실패')) {
            handleLogout();
        }
    }
}

// --- 채팅 메시지 전송 ---
sendButton.addEventListener('click', async () => {
    const message = chatInput.value.trim();
    if (!message) return;

    addMessage('You', message, 'user-message');
    chatInput.value = '';

    setChatUIEnabled(false);

    try {
        const response = await fetch(`${API_BASE_URL}/chat/simple`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('인증 실패. 다시 로그인해주세요.');
            }
            const errorData = await response.json();
            throw new Error(errorData.detail || '채팅 응답 실패');
        }

        const data = await response.json();
        const aiResponseContent = data.response;

        addMessage('AI', aiResponseContent, 'ai-message');

    } catch (error) {
        chatStatus.textContent = `채팅 오류: ${error.message}`;
        console.error('채팅 에러:', error);
        if (error.message.includes('인증 실패')) {
            handleLogout();
        }
    } finally {
        setChatUIEnabled(true);
    }
});

// --- 로그아웃 처리 ---
logoutButton.addEventListener('click', handleLogout);

function handleLogout() {
    accessToken = null;
    currentUsername = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('username');
    authSection.style.display = 'block';
    chatSection.style.display = 'none';
    chatWindow.innerHTML = '';
    loginUsernameInput.value = '';
    loginPasswordInput.value = '';
    registerUsernameInput.value = '';
    registerPasswordInput.value = '';
    registerPasswordConfirmInput.value = '';
    loginStatus.textContent = '로그아웃 되었습니다.';
    chatStatus.textContent = '';
    showAuthForm('login-form');
}

// --- 페이지 로드 시 초기화 및 자동 로그인 시도 ---
window.onload = async () => {
    const storedToken = localStorage.getItem('accessToken');
    const storedUsername = localStorage.getItem('username');
    if (storedToken && storedUsername) {
        accessToken = storedToken;
        currentUsername = storedUsername;
        loggedInUser.textContent = currentUsername;
        authSection.style.display = 'none';
        chatSection.style.display = 'block';
        await loadChatHistory();
    } else {
        showAuthForm('login-form');
    }
};