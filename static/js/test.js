let socket;
let messagesDiv = document.getElementById('messages');
let connectBtn = document.getElementById('connectBtn');
let disconnectBtn = document.getElementById('disconnectBtn');

// Function to append messages to the messages div
function appendMessage(message) {
    let p = document.createElement('p');
    p.textContent = message;
    messagesDiv.appendChild(p);
}

// Handle WebSocket connection
connectBtn.addEventListener('click', () => {
    const exchange = document.getElementById('exchange').value;
    const symbol = document.getElementById('symbol').value;

    // Open WebSocket connection
    socket = new WebSocket(`ws://localhost:8000/ws/subscribe/${exchange}/${symbol}`);

    socket.onopen = function () {
        appendMessage("WebSocket connection opened.");
        connectBtn.disabled = true;
        disconnectBtn.disabled = false;
    };

    socket.onmessage = function (event) {
        appendMessage(`Received: ${event.data}`);
    };

    socket.onerror = function (error) {
        appendMessage(`WebSocket error: ${error.message}`);
    };

    socket.onclose = function (event){
        appendMessage(`WebSocket Close: ${event.data}`);
    }
});
