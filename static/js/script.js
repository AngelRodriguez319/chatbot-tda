$(document).on('keydown', function (e) {
    if (e.which == 13) {
        getResponse();
        return false;
    }
})


$('#sendMessage').click(function(){
    getResponse();
})

const getResponse = async () => {
    
    let messageUser = $.trim($('#message').val());
    if(messageUser == '') return;
   
    let response = await fetch('/getResponse', {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        crendentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({
            message: messageUser
        })
    });

    $('#message').val('');
    let json = await response.json();

    $('#conversation').append(`
        <li class="sent">
            <img src="../static/img/user.png" alt="" >
            <p>${messageUser}</p> 
        </li>
        <li class="replies">
            <img src="../static/img/chatbot.png" alt="" >
            <p>${json['response']}</p>
        </li>
    `);
    
    $(".messages").animate({ 
        scrollTop: $(document).height() 
    }, "fast");

};