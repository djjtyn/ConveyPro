//This file contains JS relevant to specific opportunity detail pages
$(document).ready(() => {
    initStageModalListener();
    initStageModalListeners();
});


function initStageModalListener() {
    //Display the stage modal when the stage button is clicked
    $('#stageBtn').on('click', ()=> {
        $('#stageModal').modal('show');
    })
}

function initStageModalListeners() {
    initStageBtnListeners();
    initStaveSaveBtnListener();
}

function initStageBtnListeners() {
    $('#selectStageContainer .stageBtn').each(function(i, element) {
        $(element).on('click', function(e) {
            $('#selectedStage').val($(element).text());
            $('#saveStageBtn').removeClass();
            $('#saveStageBtn').addClass($(element).val());
        })
    });
}

function initStaveSaveBtnListener() {
    $('#saveStageBtn').on('click', () => {
        updateStage();
    })
}

function updateStage() {
    $('#stageModal').modal('hide');
    const selectedStage = $('#selectedStage').val();
    // Only update the stage if it differs from the one the page loaded with
    if($('#stageBtn').text() != selectedStage) {
        //Update db if selected stage differs 
        const targetURL = window.location.href;
        $('#stageBtn').removeClass();
        $('#stageBtn').addClass('stageBtn');
        $('#stageBtn').addClass(`${selectedStage.split(' ').join('')}Btn`);
        $('#stageBtn').text(selectedStage);        
        csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        let reqObj = {
            'action': 'stageUpdate',
            'stage': selectedStage
        }
        $.ajax({
            type: 'POST',
            url: targetURL,
            data: JSON.stringify(reqObj),
            processData: false,
            contentType: false,
            cache: false,
            headers: {
                'X-CSRFToken': csrfToken,
            },
            success: function(res) {
                displayUpdateStatus('success', res['message']);
            },
            error: function (e) {
                displayUpdateStatus('error', res['message']);
            },
        });
    } 
}

function displayUpdateStatus(status, msg) {
    $('#pageMessages').text(msg);
    if(status == 'error') {
        $('#pageMessages').css('background-color', 'red');
    }
    $('#pageMessages').fadeIn(500).fadeOut(3000);
}

