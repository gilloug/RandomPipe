$(document).ready(function(){

    $(".play").click(function(ev){
        window.location = "/?pipe_id=" + $(this).attr("pipe_id");
    });

    $(".downvote").click(function(ev){
        $.post("downvote",
               {
                   _id: $(this).attr("_id")
               },
               function(data, status){
                   location.reload();
               });
    });

});
