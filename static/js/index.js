$(document).ready(function() { 
    $uncheckedSiblings = $("input:checkbox:not(:checked)").siblings("input");
    $uncheckedSiblings.fadeOut();
    $("#tfidf_slider").fadeOut();

    selected_countries_list = [];
    $('.selectpicker').selectpicker();

});

$(document).ready(function () { 
    $(".selectpicker").selectpicker();
    $(".bootstrap-select").click(function () {
         $(this).addClass("open");
    });
  });



function checkpoint_change_react(){
    $uncheckedSiblings = $(".additional-filter-criteria-checkbox:checkbox:not(:checked)").siblings("input");
    $uncheckedSiblings.fadeOut();
    $checkedSiblings = $(".additional-filter-criteria-checkbox:checkbox:checked").siblings("input");
    if ($checkedSiblings.length > 0)
        $("#tfidf_slider").fadeIn();
    else    
        $("#tfidf_slider").fadeOut();
    $checkedSiblings.fadeIn();
}