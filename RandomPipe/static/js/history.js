$(document).ready(function(){

    $('.modal').modal();

    $(".play").click(function(ev){
        window.location = "/?pipe_id=" + $(this).attr("pipe_id");
    });

    $(".delete").click(function(ev){
        $.post("delete_pipe",
               {
                   _id: $(this).attr("_id")
               },
               function(data, status){
                   location.reload();
               });
    });

    $(".upvote").click(function(ev){
        $.post("upvote",
               {
                   _id: $(this).attr("_id")
               },
               function(data, status){
                   location.reload();
               });
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
