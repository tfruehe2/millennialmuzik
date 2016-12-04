var vid_id;
var dom_elem;
var player;
$(".mv-btn").click(function(e){
  e.preventDefault();
  var $this = $(this);
  $.ajax({
    url : $this.attr('data-fetch-url'),
    type : 'GET',
    success : function(json){
      var dom_elem = $this.parent('.player');
      vid_id = json.video_id;
      loadYoutubeVideo();
      console.log("success");
      console.log(vid_id);
    },
    error : function(error){
      console.log("failure");
    }

  });
});

function loadYoutubeVideo() {
    var tag = document.createElement('script');
    tag.src = "https://www.youtube.com/iframe_api";
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

}
function onYouTubeIframeAPIReady() {
    console.log(vid_id);
    player = new YT.Player('', {
            height: '390',
            width: '640',
            videoId: vid_id,
            origin: 'http://www.test1.com:8000',
            events: {
              'onReady': onPlayerReady,
              'onStateChange': onPlayerStateChange
            }
      });
      console.log("got here");
  }
  function onPlayerReady(event) {
            console.log('player ready');
            event.target.playVideo();
    }
  function onPlayerStateChange(){

  }
