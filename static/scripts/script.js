$('#form-container a').click(function(e) {
  var text = $(this).attr('sectionId');
  console.log(text);

  $.ajax({
      url: "/top_songs",
      type: "POST",
      data: {time_span: text},
      success:function(response){ replace_content(response)}


    });

});

function replace_content(response){
   $('#top_song_container').empty();

    $("#top_song_container").html(response);
}
