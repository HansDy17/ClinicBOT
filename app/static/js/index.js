function scrollToBottom() {
var messageBody = document.getElementById("messageFormeight");
messageBody.scrollTop = messageBody.scrollHeight;
}
var userId = document.getElementById("user-id").getAttribute("data-user-id");

function logout() {
// Redirect to logout page or clear session
window.location.href = "/logout"; // Update this URL based on your actual logout logic
}
function disableInput() {
    $('#text').prop('disabled', true).attr('placeholder', 'Please wait for response...');
    $('#send').prop('disabled', true);
}

function enableInput() {
    $('#text').prop('disabled', false).attr('placeholder', 'Type your message...');
    $('#send').prop('disabled', false);
}

$(document).ready(function () {
$("#messageArea").on("submit", function (event) {
    event.preventDefault();
    const startTime = Date.now();
    const date = new Date();
    const hour = date.getHours();
    const minute = date.getMinutes();
    const str_time = hour + ":" + minute;
    var rawText = $("#text").val();
    
    disableInput();

    var userHtml =
    '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' +
    rawText +
    '</div></div>';

    $("#text").val("");
    $("#messageFormeight").append(userHtml);
    scrollToBottom();

    // Add thinking message with unique ID
    var thinkingId = 'thinking-' + Date.now();
// Modify the thinking message creation in your JavaScript
    var thinkingHtml = '<div class="d-flex justify-content-start mb-4" id="' + thinkingId + '">' +
        '<div class="msg_cotainer thinking"><span class="thinking-dots">Thinking</span>' + '</div></div>';
    
    $("#messageFormeight").append(thinkingHtml);
    scrollToBottom();

// Modify the fetch handling section like this
fetch('/get', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
        msg: rawText,
        user_id: userId
    })
})
.then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    // Create unique IDs for this response
    const responseId = 'response-' + Date.now();
    const timeId = 'time-' + Date.now();
    
    // Create a reference to the thinking element
    const $thinkingElement = $("#" + thinkingId);
    let responseBuffer = '';
    let firstChunkReceived = false;

    function read() {
        return reader.read().then(({ done, value }) => {
            if (done) {
                // Final processing
                responseBuffer = responseBuffer
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
                
                $("#" + responseId).html(responseBuffer.replace(/\n/g, '<br>'));
                
                const endTime = Date.now();
                const timeTaken = ((endTime - startTime) / 1000).toFixed(1);
                $("#" + timeId).html(`(Thought for ${timeTaken}s)`);
                
                // Enable input only after full response is received
                enableInput();
                return;
            }
            
            const chunkText = decoder.decode(value, { stream: true });
            responseBuffer += chunkText;
            
            const processedText = responseBuffer
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" class="chat-link">$1</a>')
                .replace(/\n/g, '<br>');

            if (!firstChunkReceived) {
                $thinkingElement.replaceWith(`
                    <div class="d-flex justify-content-start mb-4" id="${thinkingId}">                        
                        <div class="msg_cotainer">
                            <span id="${responseId}">${processedText}</span>
                            <span class="msg_time" id="${timeId}">${str_time}</span>
                        </div>
                    </div>
                `);
                firstChunkReceived = true;
            } else {
                $("#" + responseId).html(processedText);
            }

            scrollToBottom();
            return read();
        });
    }
    
    return read();
})
.catch(error => {
    console.error('Error:', error);
    $("#" + thinkingId).html('<div class="alert alert-danger">Error getting response</div>');
    enableInput(); // Re-enable on error
});
});

$("#custom-sidebar-toggle").change(function () {
if ($(this).is(":checked")) {
    $(".chat").css("margin-left", "250px"); 
} else {
    $(".chat").css("margin-left", "0"); 
}
});

// Fetch and Display Real Appointment Date
function fetchAppointment() {
    $.ajax({
        type: "GET",
        url: "/existing_appointment/" + userId,  
        success: function (response) {
            if (response.appointment) {
                $("#appointmentDetails").text(response.appointment);
            } else {
                $("#appointmentDetails").text("You have no scheduled appointment.");
            }
        },
        error: function () {
            $("#appointmentDetails").text("Unable to fetch appointment details.");
        }
    });
}

//Fetch Appointment When the Page Loads
fetchAppointment();

//Automatically Refresh Every 10 Seconds
setInterval(fetchAppointment, 30000);  // 10,000ms = 10 seconds

// Show the dropdown on hover
$(".dropdown").hover(
    function () {
        $(this).find(".dropdown-menu").stop(true, true).delay(200).fadeIn(200);
    },
    function () {
        $(this).find(".dropdown-menu").stop(true, true).delay(200).fadeOut(200);
    }
);

}); 