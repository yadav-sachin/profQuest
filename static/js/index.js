$(document).ready(function () {
    $uncheckedSiblings = $("input:checkbox:not(:checked)").siblings("div, input");
    $uncheckedSiblings.fadeOut();
    $("#tfidf_slider").fadeOut();
    checkpoint_change_react(); 
    
    selected_countries_list = [];
    $('.selectpicker').selectpicker();
    if ($("#searchType-input").val() == "name")
    {
        $("#searhbox-container").removeClass("hue-rotate-background");
        $(".slider-container").fadeOut();
    }
    else
    {
        $("#searhbox-container").addClass("hue-rotate-background");
        $(".slider-container").fadeIn();
    }

    $("#searchType-input").change(function () {
        if ($("#searchType-input").val() == "name")
        {
            $("#searhbox-container").removeClass("hue-rotate-background");
            $(".slider-container").fadeOut();
        }
        else
        {
            $("#searhbox-container").addClass("hue-rotate-background");
            $(".slider-container").fadeIn();
        }
    });
});

$(document).ready(function () {
    $(".selectpicker").selectpicker();
    $(".bootstrap-select").click(function () {
        $(this).addClass("open");
    });
});



function checkpoint_change_react() {
    $uncheckedSiblings = $(".additional-filter-criteria-checkbox:checkbox:not(:checked)").siblings("div, input");
    $uncheckedSiblings.fadeOut();
    $checkedSiblings = $(".additional-filter-criteria-checkbox:checkbox:checked").siblings("div, input");
    if ($checkedSiblings.length > 0)
        $("#tfidf_slider").fadeIn();
    else
        $("#tfidf_slider").fadeOut();
    $checkedSiblings.fadeIn();
}