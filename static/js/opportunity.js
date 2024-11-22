//This file contains JS relevant to specific opportunity detail pages
$(document).ready(() => {
    initStageModalListener();
    initStageModalListeners();
    initSubStageListeners();
    initNoteListeners();
    initDocListeners();
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
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
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
            updateCompletionCount(inputName, 'increment', element.id);
            updateSubStage(inputName,selectedVal, element.id);
        }
    } else {
        // SomeDate inputs may have potential to be set as NA
        if(onlyDateInputApplicable(inputName)) {
            updateSubStage(inputName,selectedVal, element.id);
        } else {
            //Handle inputs which can be changed back to NA
            if(!selectedVal) {
                //Display the N/A select options again
                updateCompletionCount(inputName, 'decrement', element.id)
                selectEl = createSelectInputElement(parentElement, element, element.id, inputName);
                //Remove the input element from the DOM to avoid duplicate element ID
                element.remove();
                parentElement.appendChild(selectEl);
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
            //Remove any checks that previosuly existed for the input
            updateCompletionCount(inputName, 'decrement', elId);
            selectEl = createSelectInputElement(parentElement, element, elId, inputName)
            input.remove();
            parentElement.appendChild(selectEl);
        } else {
            updateCompletionCount(inputName, 'increment', elId);
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
            updateCompletionCount(inputName, res['renderCount'], id);
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

function updateCompletionCount(inputName, opType, id) {
    // Update the stage completion count if the db value has been added or removed
    if (opType == 'increment' || opType == 'decrement') {
        const substageWrapId = getRelatedSubStageWrapId(inputName)
        const completionCountEl = $(`#${substageWrapId} .completetionCount`);
        let currentCompletionCount = Number(completionCountEl.text());
        opType == 'increment' ? currentCompletionCount++ : currentCompletionCount--;
        completionCountEl.text(currentCompletionCount);
        opType == 'increment' ? renderCheckIcon(id, 'check') : renderCheckIcon(id, 'remove')
    } 
    if(opType == 'static') {
        renderCheckIcon(id, 'check');
    } 
}

function getRelatedSubStageWrapId(inputName) {
    if (inputName == 'title_deed_send_date' || inputName == 'closing_requirements_received_date' || inputName == 'closing_requirements_returned_date') {
        return 'contractsExchangedSubStageWrap'
    }
    return 'saleAgreedSubStageWrap'
}

function onlyDateInputApplicable(inputName) {
    switch (inputName) {
        case 'contracts_issued_to_purchaser':
        case 'contracts_received_date':
        case 'deposit_received_date':
        case 'closing_requirements_received_date':
        case 'closing_requirements_returned_date':
        case 'title_deed_send_date':
            return true;       
        default:
            return false;
    }
}

function initNoteListeners() {
    initNoteAreaListener();
    initAddNoteListener();
    initNoteFormListeners();
    initExistingNoteListeners();
}

function initNoteAreaListener() {
    $('#viewNoteBtn').on('click', ()=> {
        toggleNoteDocArea('note')
    })
}

function initAddNoteListener() {
    $('#addNoteBtn').on('click', function (e) {
        $(this).css('display', 'none')
        $('#noteEntryForm').css('display', 'block');
    }) 
}

function initNoteFormListeners() {
    $('#cancelNoteBtn').on('click', () => {
        cancelNote();
    }) 
    $('#saveNoteBtn').on('click', () => {
        createNewNote();
    })
}

function cancelNote() {
    $('#noteEntryForm').css('display', 'none');
    $('#addNoteBtn').css('display', 'block');
    $('#noteContent').removeClass('missingNoteData');
    $('#noteContent').attr('placeholder', 'Note Content');
    $('#noteContent').val('');
    $('#noteTitle').removeClass('missingNoteData');
    $('#noteTitle').attr('placeholder', 'Note Title');
    $('#noteTitle').val('');
}

function createNewNote() {
    if (all_inputs_populated()) {
        const noteTitle = $('#noteTitle').val();
        const noteContent =$('#noteContent').val();
        processNote('create',noteTitle, noteContent, null);
    }
}

function all_inputs_populated() {
    populated = true;
    if($('#noteContent').val() == '') {
        $('#noteContent').addClass('missingNoteData');
        $('#noteContent').attr('placeholder', 'Content Required');
        populated = false;    
    }
    if(!$('#noteTitle').val()) {
        $('#noteTitle').addClass('missingNoteData');
        $('#noteTitle').attr('placeholder', 'Title Required');
        populated = false
    }
    return populated;
}

function processNote(action, noteTitle, noteContent, id) {
    const targetURL = window.location.href;
    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    let reqObj = {
        'action': 'actionNote',
        'actionType': action,
        'title': noteTitle,
        'value': noteContent,
    }
    if (action != 'create') {
        reqObj.noteId = id;
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
            $('#noteDeleteModal').modal('hide');
            const noteId = res['affectedNoteId']
            displayUpdateStatus('success', res['message'])
            if (action == 'create') {
                //Increment counter, append note to note list and hide note entry area
                updateNoteCounter(res['renderCount']);
                renderNewNote(noteId, noteTitle,noteContent);
                cancelNote();
            }
            if(res['renderCount'] == 'decrement') {
                removeNote(noteId);
                updateNoteCounter(res['renderCount']);
            }
        },
        error: function (e) {
            console.log('Error at processNoteSave(): ' + e);
        },
    });
}

function renderNewNote(noteId, noteTitle,noteContent) {
    const form = $(`
        <form>
            <input type="text" value = '${noteId}' class = 'noteId' disabled hidden>
            <input type="text" class="form-control-plaintext noteTitle" value = '${noteTitle}' disabled>
            <textarea class="form-control-plaintext noteContent" value = '${noteContent}' disabled>${noteContent}</textarea>
            </form>
    `)
    form.append(renderNoteButtons(form));
    $('#existingNotes').prepend(form);
}

function renderNoteButtons(parentForm) {
    const btnWrap = document.createElement('div');
    btnWrap.setAttribute('class', 'row');
    buttons = ['delete','edit'];
    for(let i=0;i<buttons.length;i++) {
        const btn = document.createElement('button');
        btn.setAttribute('type', 'button');
        const colElement = document.createElement('div');
        colElement.setAttribute('class', 'col-sm-6');
        let className = 'deleteNoteBtn';
        let btnInner = '<i class="fa fa-trash" aria-hidden="true"></i>';
        //Delete btn wil lbe at index 0
        if(i==0) {
            btn.addEventListener('click', function() {
                displayNoteDeletionModel(btn);
            })
        } else {
            //edit btn index
            className = 'editNoteBtn';
            btnInner = '<i class="fas fa-edit" aria-hidden="true"></i>';
            btn.addEventListener('click', function() {
                displayAsEditableNote(parentForm)
            })
        }
        btn.setAttribute('class', className);
        btn.innerHTML = btnInner;
        colElement.appendChild(btn);
        btnWrap.appendChild(colElement);
    }
    return btnWrap;
}

function updateNoteCounter(action) {
    const noteCounter = $('#noteCounter');
    let currentNoteCount = Number(noteCounter.text());
    action == 'increment'? currentNoteCount++: currentNoteCount--;
    noteCounter.text(currentNoteCount);
}

function removeNote(noteId) {
    $(`input[value="${noteId}"]`).closest('form').remove();
}

function initExistingNoteListeners() {
    initNoteEdit();
    initNoteDelete();
}

function initNoteEdit() {
    $('#existingNotes .editNoteBtn').each(function(i, element) {
        $(element).on('click', () => {
            const parentForm = $(element).closest('form');
            displayAsEditableNote(parentForm);   
        })
    });
}

function displayAsEditableNote(parentForm) {
    const noteTitle = parentForm.find('.noteTitle');
    const noteContent = parentForm.find('.noteContent');
    const deleteNoteBtn = parentForm.find('.deleteNoteBtn');
    const editNoteBtn = parentForm.find('.editNoteBtn');
    const originalTitleVal = noteTitle.val();
    const originalContentVal = noteContent.val();
    noteTitle.removeAttr('disabled');
    noteContent.removeAttr('disabled');
    deleteNoteBtn.css('display', 'none');
    editNoteBtn.css('display', 'none');

    if(parentForm.find('.noteEditActions').length > 0) {
        parentForm.find('.cancelEditBtn').css('display', 'block');
        parentForm.find('.saveEditBtn').css('display', 'block');
        return;
    }
    // Will create
    createNoteEditButtons(parentForm, noteTitle, noteContent, deleteNoteBtn, editNoteBtn, originalTitleVal, originalContentVal);
}

function createNoteEditButtons(parentForm, noteTitle, noteContent, deleteNoteBtn, editNoteBtn, originalTitleVal, originalContentVal) {
    const btnArea = parentForm.find('.row');
    btnArea.find('.col-sm-6').each(function(i, element) {
        const newBtn = document.createElement('button');
        newBtn.setAttribute('type', 'button');
        //Render first element as cancel button
        if(i == 0) {
            newBtn.innerHTML = 'Cancel';
            newBtn.setAttribute('class', 'cancelEditBtn');
            newBtn.addEventListener('click', ()=> {
                cancelNoteEdit(parentForm, noteTitle, noteContent, deleteNoteBtn, editNoteBtn, originalTitleVal, originalContentVal);
            })
        } else {
            newBtn.innerHTML = 'Save'
            newBtn.setAttribute('class', 'saveEditBtn');
            newBtn.addEventListener('click', () => {
                editNote(parentForm, noteTitle.val(), noteContent.val());
                cancelNoteEdit(parentForm, noteTitle, noteContent, deleteNoteBtn, editNoteBtn, null, null);
            })
        }
        element.appendChild(newBtn);
    })
    btnArea.addClass('noteEditActions');
}

function cancelNoteEdit(parentForm, noteTitle, noteContent, deleteNoteBtn, editNoteBtn, originalTitleVal, originalContentVal) {
    parentForm.find('.cancelEditBtn').css('display', 'none');
    parentForm.find('.saveEditBtn').css('display', 'none');
    deleteNoteBtn.css('display', 'block');
    editNoteBtn.css('display', 'block');
    //Revert to values prior to clicking the edit button
    if(originalTitleVal) {
        noteTitle.val(originalTitleVal);
    }
    if(originalContentVal) {
        noteContent.val(originalContentVal);
    }
    noteTitle.prop('disabled', true);
    noteContent.prop('disabled', true);
}

function editNote(parentForm, noteTitle, noteContent) {
    //Get the note id
    const noteId = parentForm.find('.noteId').val();
    processNote('update',noteTitle, noteContent, noteId)
}

function initNoteDelete() {
    $('#cancelNoteDeletionBtn').on('click', () => {
        $('#noteDeleteModal').modal('hide');
    })
    $('#existingNotes .deleteNoteBtn').each(function(i, element) {
        $(element).on('click', () => {
            displayNoteDeletionModel(element);
        });
    });
}

function displayNoteDeletionModel(element) {
    const parentForm = $(element).closest('form');
    $('#noteDeleteModal').modal('show');
    //Unbind the current event handler from the delete confimation btn to allow selected note id to be passed in new event handler
    $('#confirmNoteDeletionBtn').unbind('click');
    $('#confirmNoteDeletionBtn').on('click', () => {
        const noteId = parentForm.find('.noteId').val();
        deleteNote(noteId);
    })
}


function deleteNote(noteId) {
    processNote('delete',null, null, noteId)
}

function toggleNoteDocArea(visibleTarget) {
    if(visibleTarget == 'note') {
        $('#noteWrap').show();
        $('#docWrap').hide()
    } else {
        $('#docWrap').show();
        $('#noteWrap').hide();
    }
}

function initDocListeners() {
    initDocumentAreaListener();
}

function initDocumentAreaListener() {
    $('#viewDocBtn').on('click', ()=> {
        toggleNoteDocArea('document')
    })
}


