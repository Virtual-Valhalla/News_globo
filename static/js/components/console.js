/* ════════════════════════════════════════════════════════════════════ */
/* CONSOLE COMPONENT — logToConsole, clearConsole, toggleConsole       */
/* ════════════════════════════════════════════════════════════════════ */

let isConsoleCollapsed = false;

function getTimeStamp() {
    const now = new Date();
    return `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
}

function logToConsole(message, type = 'info', details = '') {
    const timestamp = getTimeStamp();
    const typeMap = {
        'error':   { icon: '🔴', label: 'ERROR',   class: 'msg-error' },
        'warning': { icon: '🟡', label: 'WARNING',  class: 'msg-warning' },
        'success': { icon: '🟢', label: 'SUCCESS',  class: 'msg-success' },
        'info':    { icon: '🔵', label: 'INFO',     class: 'msg-info' },
        'debug':   { icon: '⚫', label: 'DEBUG',    class: 'msg-debug' },
    };
    const typeInfo = typeMap[type] || typeMap['info'];
    console.log(`[${timestamp}] ${typeInfo.icon} ${typeInfo.label}: ${message}`, details);

    const msgEl = document.createElement('div');
    msgEl.className = `console-message ${typeInfo.class}`;
    msgEl.innerHTML = `
        <span class="console-time">[${timestamp}]</span>
        <span class="console-type">${typeInfo.icon} ${typeInfo.label}</span>
        <span>${message}</span>
    `;

    const consoleContent = document.getElementById('console-content');
    consoleContent.appendChild(msgEl);

    const messages = consoleContent.querySelectorAll('.console-message');
    if (messages.length > 50) messages[0].remove();
    consoleContent.scrollTop = consoleContent.scrollHeight;
}

function clearConsole() {
    document.getElementById('console-content').innerHTML = '';
    logToConsole('Consola limpiada', 'info');
}

function toggleConsole() {
    const consoleEl = document.getElementById('error-console');
    const btn       = document.getElementById('collapse-btn');
    isConsoleCollapsed = !isConsoleCollapsed;
    consoleEl.classList.toggle('console-collapsed', isConsoleCollapsed);
    btn.textContent = isConsoleCollapsed ? '+' : '−';
}
