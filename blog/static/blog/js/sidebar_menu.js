$("#menu-toggle").click(function(e){
  e.preventDefault();
  $("#wrapper").toggleClass("toggled");
});
$("#menu-toggle-2").click(function(e){
  e.preventDefault();
  $("#wrapper").toggleClass("toggled-2");
  $("#menu ul").hide();
  setTimeout(function() {
    window.dispatchEvent(new Event('resize'));
  },300);

});

function initMenu() {
  $('#menu ul').hide();
  $('#menu ul').children('.current').parent().show();
  $('#menu li a').click(
    function() {
      var checkElement = $(this).next();
      if((checkElement.is('ul')) && (checkElement.is(':visible'))) {
        return false;
      }
      if ((checkElement.is('ul')) && (!checkElement.is(':visible'))) {
        $('#menu ul:visible').slideUp('normal');
        checkElement.slideDown('normal');
        return false;
      }
    }
  );
  $('body').addClass('loaded');
}
$(document).ready(function() {
  initMenu();
});
