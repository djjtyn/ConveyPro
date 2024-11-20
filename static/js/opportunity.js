//This file contains JS relevant to specific opportunity detail pages
$(document).ready(() => {
    initStageModalListener();
    initStageModalListeners();
    initSubStageListeners();
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
        const targetURL = window.location.href;
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
                renderSelectedStage(selectedStage);
                displayUpdateStatus('success', res['message']);
            },
            error: function (e) {
                displayUpdateStatus('error', res['message']);
            },
        });
    } 
}

function renderSelectedStage(selectedStage) {
    $('#stageBtn').removeClass();
    $('#stageBtn').addClass('stageBtn');
    $('#stageBtn').addClass(`${selectedStage.split(' ').join('')}Btn`);
    $('#stageBtn').text(selectedStage);  
    if(selectedStage == 'Sale Agreed') {
        $('#contractsExchangedSubStageWrap').attr('hidden', true);
        $('#saleAgreedSubStageWrap').removeAttr('hidden');
    } else if(selectedStage == 'Contracts Exchanged')  {
        $('#saleAgreedSubStageWrap').attr('hidden', true);
        $('#contractsExchangedSubStageWrap').removeAttr('hidden');
    } else {
        $('#contractsExchangedSubStageWrap').attr('hidden', true);
        $('#saleAgreedSubStageWrap').attr('hidden', true);
    }
}

function displayUpdateStatus(status, msg) {
    $('#pageMessages').text(msg);
    if(status == 'error') {
        $('#pageMessages').css('background-color', 'red');
    }
    $('#pageMessages').fadeIn(500).fadeOut(3000);
}

function initSubStageListeners() {
    //Get all substage input and select elements
    $('#saleAgreedSubStageWrap input, #saleAgreedSubStageWrap select, #contractsExchangedSubStageWrap input, #contractsExchangedSubStageWrap select').each(function(i, element) {
        const elementType = $(element).is('input') ? 'input': 'select';
        $(element).on('change', function(e) {
            processSubStageUpdate(this, elementType);
        })
    })
}

function processSubStageUpdate(element, elementType) {
    const selectedVal = element.value;
    const inputName = element.name;
    const parentElement = element.parentNode;
    //Determine if input type needs to change from select element to date element
    if (elementType == 'select') {
        //Display a date input instead of a select element and append it to the select elements parent
        if(selectedVal == 'date') {
            const dateInput = createDateInputElement(parentElement,element,element.id, inputName);   //Create a date input with an id value matching the select element and the ability to revert to original element
            //Remove the select element from the DOM to avoid duplicate element ID
            renderCheckIcon(element.id, 'uncheck');
            element.remove();
            parentElement.appendChild(dateInput);
        } else {
            updateSubStage(inputName,selectedVal, element.id)
        }
    } else {
        // SomeDate inputs may have potential to be set as NA
        if(onlyDateInputApplicable(inputName)) {
            updateSubStage(inputName,selectedVal, element.id);
        } else {
            //Handle inputs which can be changed back to NA
            if(!selectedVal) {
                //Display the N/A select options again
                selectEl = createSelectInputElement(parentElement, element, element.id, inputName);
                //Remove the input element from the DOM to avoid duplicate element ID
                element.remove();
                parentElement.appendChild(selectEl);
                //Remove any checks that previosuly existed for the input
                renderCheckIcon(selectEl.id, 'uncheck');
            } else {
                updateSubStage(inputName,selectedVal, element.id);
            }
        }
    }
}

function createDateInputElement(parentElement, element, elId, inputName) {
    const input = document.createElement('input');
    input.setAttribute('type', 'date');
    input.setAttribute('id', elId);
    input.setAttribute('name', inputName);
    //Event handler to revert to select input
    input.addEventListener('input', function() {
        //If clear button has been selected revert back to the original select element
        if (!this.value) {
            selectEl = createSelectInputElement(parentElement, element, elId, inputName)
            input.remove();
            parentElement.appendChild(selectEl);
            //Remove any checks that previosuly existed for the input
            renderCheckIcon(element.id, 'uncheck');
        } else {
            // Update Db with selected value
            updateSubStage(element.name,this.value, elId);
        }
    })
    return input;
}

function createSelectInputElement(parentElement, element, elId, inputName) {
    const select = document.createElement('select');
    select.setAttribute('type', 'date');
    select.setAttribute('id', elId);
    select.setAttribute('name', inputName);
    select.innerHTML = 
    `
        <option disabled selected>Select a Value</option>
        <option value="NA">N/A</option>
        <option value="date">Select a Date</option>
    `;
    select.addEventListener('change', function(e) {
        processSubStageUpdate(select, 'select');
    })
    return select;
}

function updateSubStage(inputName, val, id) {
    const targetURL = window.location.href;
    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    let reqObj = {
        'action': 'subStageUpdate',
        'subStageName': inputName,
        'value': val,
        'inputId': id
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
            renderCheckIcon(id, 'check');
            displayUpdateStatus('success', res['message']);
        },
        error: function (e) {
            displayUpdateStatus('error', res['message']);
        },
    });
}

function renderCheckIcon(id, action) {
    const timelineElement = document.getElementById(id).parentNode.parentNode.parentNode
    const iconWrap = timelineElement.querySelector('.timeLineIcon');
    const innerHtml = action =='check' ? `<i class="fa-solid fa-circle-check"></i>` : ''
    iconWrap.innerHTML = innerHtml;
}

function onlyDateInputApplicable(inputName) {
    if (inputName == 'contracts_issued_to_purchaser' || inputName == 'contracts_received_date' || inputName == 'deposit_received_date' ) {
        return true;
    }
    return false;
}


