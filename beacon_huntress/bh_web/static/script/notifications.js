function getNotificationsAlgo(url, containerId){
    
    console.log("Setting up WebSocket connection to:", url);
    const socket = new WebSocket(url);
  
    socket.onmessage = function (e) {

        const data = JSON.parse(e.data);
        console.log('Message received:', data);
  
        // CREATE THE ALERT
        const alertDiv = document.createElement('div');
        alertDiv.role = 'alert';
        alertDiv.style.padding = '15px';
  
        // SET THE MESSAGE CONTENT
        alertDiv.innerHTML = `
            ${data.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        if (data.cnt == 0) {
            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        } else {
            alertDiv.className = 'alert alert-success alert-dismissible fade show';
        }
  
        // APPEND THE ALERT
        const container = document.getElementById(containerId) || document.body
        container.appendChild(alertDiv);
    };
  
    socket.onerror = function (error) {
        console.error('WebSocket error:', error);
    };

    socket.onclose = function () {
        console.log("WebSocket connection closed from:", url);
    };
}