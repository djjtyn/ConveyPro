//This file contains JS relevant to the webpage which lists all opportunities
$(document).ready(() => {
    initFilters();
    initRecordRedirect();
});


function initFilters() {
    initBedFilterListener();
    initStageFilterListener();
    initDaysInStageListener();
}

function initBedFilterListener() {
    $('#bedFilterSelect').on('change', function() {
        applyBedFilter($(this).val());
    });
}

function applyBedFilter(filterBy) {
    $('.oppListItem').each(function(i, element){
        const stageFilter = $('#stageFilterSelect').val();
        const idleTimeFilter =  $('#timeFilterSelect').val();
        if(filterBy == 'allBeds') {
            //If the all beds filter is selected with no other filters applied show all elements
            if(stageFilter == 'allStages' && idleTimeFilter == 'allTimes') {
                $(element).show();
            } else {
                if(stageFilter != 'allStages' && idleTimeFilter != 'allTimes' ) {
                    //Stage and Idle Time Filters already applied
                    $(element).hasClass(stageFilter) && $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide();
                }
                if (stageFilter != 'allStages' && idleTimeFilter == 'allTimes') {
                    //Stage Filter already applied
                    $(element).hasClass(stageFilter)? $(element).show() : $(element).hide(); 
                }
                if (stageFilter == 'allStages' && idleTimeFilter != 'allTimes') {
                    //Idle time Filter already applied
                    $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide(); 
                }
            }
        } else {
            //Determine what elements to show by detecting all selected filters 
            if(stageFilter == 'allStages' && idleTimeFilter == 'allTimes') {
                //Bed filter only applied
                $(element).hasClass(filterBy) ? $(element).show() : $(element).hide(); 
            } else {
                if (stageFilter != 'allStages' && idleTimeFilter != 'allTimes') {
                    //Bed, Stage and Idle Time filters applied
                    $(element).hasClass(filterBy) && $(element).hasClass(stageFilter) && $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide();
                }
                if (stageFilter != 'allStages' && idleTimeFilter == 'allTimes') {
                    //Bed and Stage Filter
                    $(element).hasClass(filterBy) &&  $(element).hasClass(stageFilter)? $(element).show() : $(element).hide(); 
                }
                if (stageFilter == 'allStages' && idleTimeFilter != 'allTimes') {
                    //Bed and Idle time Filter
                    $(element).hasClass(filterBy) &&  $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide(); 
                }
            }
        }       
    })
}

function initStageFilterListener() {
    $('#stageFilterSelect').on('change', function() {
        applyStageFilter($(this).val());
    })
}

function applyStageFilter(filterBy) {
    $('.oppListItem').each(function(i, element){
        const bedFilter = $('#bedFilterSelect').val();
        const idleTimeFilter =  $('#timeFilterSelect').val();
        if(filterBy == 'allStages') {
            //If the all stages filter is selected with no other filters applied show all elements
            if(bedFilter == 'allBeds' && idleTimeFilter == 'allTimes') {
                console.log('Show All');
                $(element).show();
            } else {
                if(bedFilter != 'allBeds' && idleTimeFilter != 'allTimes' ) {
                    //Bed and Idle Time Filters already applied
                    $(element).hasClass(bedFilter) && $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide();
                }
                if (bedFilter != 'allBeds' && idleTimeFilter == 'allTimes') {
                    //Bed Filter already applied
                    $(element).hasClass(bedFilter)? $(element).show() : $(element).hide(); 
                }
                if (bedFilter == 'allBeds' && idleTimeFilter != 'allTimes') {
                    //Idle time Filter already applied
                    $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide(); 
                }
            }
        } else {
            //Determine what elements to show by detecting all selected filters 
            if(bedFilter == 'allBeds' && idleTimeFilter == 'allTimes') {
                //Bed filter only applied
                $(element).hasClass(filterBy) ? $(element).show() : $(element).hide(); 
            } else {
                if (bedFilter != 'allBeds' && idleTimeFilter != 'allTimes') {
                    //Bed, Stage and Idle Time filters applied
                    $(element).hasClass(filterBy) && $(element).hasClass(bedFilter) && $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide();
                }
                if (bedFilter != 'allBeds' && idleTimeFilter == 'allTimes') {
                    //Bed and Stage Filter
                    $(element).hasClass(filterBy) &&  $(element).hasClass(bedFilter)? $(element).show() : $(element).hide(); 
                }
                if (bedFilter == 'allBeds' && idleTimeFilter != 'allTimes') {
                    //Bed and Idle time Filter
                    $(element).hasClass(filterBy) &&  $(element).hasClass(idleTimeFilter)? $(element).show() : $(element).hide(); 
                }
            }
        }     
    })
}

function initDaysInStageListener(filterBy) {
    $('#timeFilterSelect').on('change', function() {
        applyStageTimeFilter($(this).val());
    })
}

function applyStageTimeFilter(filterBy) {
    $('.oppListItem').each(function(i, element){
        const stageFilter = $('#stageFilterSelect').val();
        const bedFilter =  $('#bedFilterSelect').val();
        //If the allbeds filter is selected show all elements
        if(filterBy == 'allTimes') {
            //If the all beds times is selected with no other filters applied show all elements
            if(stageFilter == 'allStages' && bedFilter == 'allBeds') {
                $(element).show();
            } else {
                if(stageFilter != 'allStages' && bedFilter != 'allBeds' ) {
                    //Stage and bed Filters already applied
                    $(element).hasClass(stageFilter) && $(element).hasClass(bedFilter)? $(element).show() : $(element).hide();
                }
                if (stageFilter != 'allStages' && bedFilter == 'allBeds') {
                    //Stage Filter already applied
                    $(element).hasClass(stageFilter)? $(element).show() : $(element).hide(); 
                }
                if (stageFilter == 'allStages' && bedFilter != 'allBeds') {
                    //Idle time Filter already applied
                    $(element).hasClass(bedFilter)? $(element).show() : $(element).hide(); 
                }
            }
        } else {
            //Determine what elements to show by detecting all selected filters 
            if(stageFilter == 'allStages' && bedFilter == 'allBeds') {
                //Idle time filter only applied
                $(element).hasClass(filterBy) ? $(element).show() : $(element).hide(); 
            } else {
                if (stageFilter != 'allStages' && bedFilter != 'allBeds') {
                    //Bed, Stage and Idle Time filters applied
                    $(element).hasClass(filterBy) && $(element).hasClass(stageFilter) && $(element).hasClass(bedFilter)? $(element).show() : $(element).hide();
                }
                if (stageFilter != 'allStages' && bedFilter == 'allBeds') {
                    //Bed and Stage Filter
                    $(element).hasClass(filterBy) &&  $(element).hasClass(stageFilter)? $(element).show() : $(element).hide(); 
                }
                if (stageFilter == 'allStages' && bedFilter != 'allBeds') {
                    //Bed and Idle time Filter
                    $(element).hasClass(filterBy) &&  $(element).hasClass(bedFilter)? $(element).show() : $(element).hide(); 
                }
            }
        }
    })
}

function initRecordRedirect() {
    $('.oppListItem').each(function(i, element) {
        $(element).on('click', function(e) {
            elementRedirectUrl = $(element).find('.redirectUrl').attr('href');
            window.location.href = `${window.location.origin}${elementRedirectUrl}`;
        })
    });
}