$(document).ready(function() {
  $(".pull_factor").change(function() {
    show_save_btn($(this));
  })
})

function show_save_btn(eventer) {
  next_sibling = eventer.next();
  next_sibling.find('button').removeClass("btn-danger");
  next_sibling.find('button').addClass("btn-info");
  next_sibling.find('button').find('i').removeClass("fa-times");
  next_sibling.find('button').find('i').addClass("fa-check");
  class_name = eventer.parent().prev().html();
  pull_factor =  eventer.val();
  next_sibling.prop("href", "javascript:update_class('"+class_name+"', "+pull_factor+");");
}

function update_class(name, pull_factor) {
  $.ajax({
        url: "/competitors/classes/update/"+name+"/",
        type: 'POST', // This is the default though, you don't actually need to always mention it,
        data: {
          pull_factor: pull_factor
        },
        success: function(data) {
            window.location = "/competitors/setup/";
            console.log(data);
        },
        failure: function(data) {
            console.log('Got an error dude');
        }
  });
}