function scrollToBottom() {
var messageBody = document.getElementById("messageFormeight");
messageBody.scrollTop = messageBody.scrollHeight;
}

function logout() {
// Redirect to logout page or clear session
window.location.href = "/logout"; // Update this URL based on your actual logout logic
}

$(document).ready(function () {
$("#messageArea").on("submit", function (event) {
    event.preventDefault();
    
    const date = new Date();
    const hour = date.getHours();
    const minute = date.getMinutes();
    const str_time = hour + ":" + minute;
    var rawText = $("#text").val();

    var userHtml =
    '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' +
    rawText +
    '<span class="msg_time_send">' +
    str_time +
    '</span></div><div class="img_cont_msg"><img src="static/img/alab.png" alt="User Avatar" class="rounded-circle user_img_msg"></div></div>';

    $("#text").val("");
    $("#messageFormeight").append(userHtml);

    scrollToBottom();

    $.ajax({
    type: "POST",
    url: "/get",
    data: { msg: rawText },
    success: function (response) {
        var botReply = typeof response === "object" ? response.response : response;  // Extract text
        botReply = botReply.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

        var botHtml =
            '<div class="d-flex justify-content-start mb-4">' +
            '<div class="img_cont_msg"><img src="static/img/nurse.png" class="rounded-circle user_img_msg"></div>' +
            '<div class="msg_cotainer">' +
            botReply +  // ✅ Properly formatted response
            '<span class="msg_time">' + str_time + "</span></div></div>";

    $("#messageFormeight").append($.parseHTML(botHtml));
        scrollToBottom();
    },
    error: function () {
        alert("Error connecting to server.");
    },
    });
});

$("#custom-sidebar-toggle").change(function () {
if ($(this).is(":checked")) {
    $(".chat").css("margin-left", "250px"); 
} else {
    $(".chat").css("margin-left", "0"); 
}
});

var appointmentDate = "Monday, March 1 at 10 am"; // Replace this with a real API call

// Update the dropdown when the page loads
if (appointmentDate) {
$("#appointmentDetails").text("You have an upcoming appointment on " + appointmentDate + ".");
} else {
    $("#appointmentDetails").text("You have no scheduled appointment.");
}

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