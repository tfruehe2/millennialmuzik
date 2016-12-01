$(function() {

  $('.playlist-button').click(function(e){
    e.preventDefault();
    var name = $(this).attr('data-song-name');
    var songID = $(this).attr('data-song-id');
    var urlString = '/create_playlist/'+songID+'/'
    console.log(urlString)
    $('#playlistForm, #playlistModal').attr('action', urlString)

    $('#songName', "#playlistModal")
        .text("Song to be added: "+name);
    $('#playlistModal')
        .attr('data-song-id', songID)
        .modal('show');

  });

  $('#playlistImage').change(function(){
    var re = new RegExp("^(image/.{3,4})$")
    var file = this.files[0]
    if (!re.test(file.type)) {
      alert('Sorry, the file you added was not an image!');
      $(this).val("");
    }
    else if (file.size >= 2000000) {
      alert('Sorry, your image file is too big!\n2Mbs is the cutoff')
      $(this).val('');
    }
  });

  $('#submitPlaylist').click(function(e) {
    console.log('clicked')
    e.preventDefault();
    var form = $('#playlistForm, #playlistModal').serialize()

    $.ajax({
      url: $('#playlistForm, #playlistModal').attr('action'),
      type: "POST",
      data: form,
      dataType: 'json',
      success: function(data) {
        if (data.e) {
          console.log(data.e)
          if(data.name != ""){
              $("#playlistName",'#playlistForm').val(data.name);
              $('#nameError', "#playlistForm").hide()
          } else {
                $('#nameError', "#playlistForm").show()
          }
          if(data.description != ""){
              $("#playlistDescription",'#playlistForm').val(data.description);
              $('#descriptionError', "#playlistForm").hide()

          } else {
              $('#descriptionError', "#playlistForm").show()
          }
        } else {
          $('#closeModal', "#playlistModal").trigger('click')
          location.reload();
        }
      },
      error: function() {
        console.log('failed to create playlist');
      }
    })

  });

  $('#addToPlaylistBtn').click(function(e) {
    e.preventDefault();
    var playlist_id = $('#playlistButtonGroup > .active', '#playlistModal').attr('data-playlist-id')
    var song_id = $("#playlistModal").attr('data-song-id')
    console.log(playlist_id)
    if (playlist_id) {
      $('#addToPlaylistError').hide()
    $.ajax({
      url: "{% url 'blog:add_to_playlist' %}",
      type: "POST",
      data: {playlist_id: $('#playlistButtonGroup > .active', '#playlistModal').attr('data-playlist-id'),
              song_id: $("#playlistModal").attr('data-song-id')},
      success: function() {
        $('#closeModal', "#playlistModal").trigger('click')
      },
      error: function() {

      },
    });
  } else {
    $('#addToPlaylistError').show()
  }
  });


  $('#playlistModalBtnGroup').click(function(e) {
    e.preventDefault();
    if (!$(e.target).hasClass('active')) {
      $(e.target)
      .addClass('active')
      .trigger('updateModalBody')
      .siblings()
      .removeClass("active");
    }

  });


  $('#createPlaylist').on('updateModalBody', function(e) {
    console.log('create playlist clicked')
    $('#submitPlaylist')
        .text('Create Playlist')
        .removeClass('add')
        .addClass('create');
    $('#playlistList').empty()
    $('#modalForm', '#playlistModal').toggle()
    $("#createPlaylistBtn").toggle()
    $('#addToPlaylistBtn').hide()

  })
  $('#addToPlaylist').on('updateModalBody', function(e) {
    console.log('AddTo playlist clicked')
    $('#modalForm', '#playlistModal').hide()
    $("#createPlaylistBtn").hide()
    $('#addToPlaylistBtn').toggle()
    $.ajax({
      url: "{% url "blog:user_playlists" pk=user.pk %}",
      type: "GET",
      success: function(data) {
        $('#playlistList', '#playlistModal').html(data)

      },
      error: function() {
        console.log('failed to retrieve users playlists');
      }
    });
  });
});
