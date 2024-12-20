function getNotifications(){
    console.log("Made it")
    const socket = new WebSocket('ws://localhost:8000/ws/notifications/');
  
    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log('Message received:', data); // Check if messages are logged here
        alert(data.message); // Show the message in an alert
    };
  
    socket.onerror = function (error) {
        console.error('WebSocket error:', error);
    };    
}