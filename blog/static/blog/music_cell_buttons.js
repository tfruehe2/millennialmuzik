$(".mv-btn").click(function(e) {
      e.preventDefault();
      var $this = $(this);
      var embed = "https://www.youtube.com/embed/ID?autoplay=1";
      var $iframe = $("<iframe>", {
        src: embed.replace("ID", $this.attr('data-id')),
        width: "280",
        height: "210",
        origin: "http://millennialsmusic.com/",
        frameborder: "0",
        allowfullscreen: "1"
      });
      var $parent = $this.parent('.panel-body');
      $parent.closest('.row').find('#lyric-scroller').css('height','240px')
      $parent.empty().append($iframe);
      $.ajax({
        url : $this.attr('data-view-url'),
        type : 'POST',
        data : {"vid_id": $this.attr('data-id')},
        success : function(json){
          $parent.closest('div.youtube-player').next().find('strong.view-count').text("Views: " + json.views);
        },
        error : function(error){
          console.log("failure");
        }

      });
  });
