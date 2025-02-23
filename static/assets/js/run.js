var connectionString = 'ws://' + window.location.host + '/ws/rs232/' + 'room_rs232' + '/';
var webSocket = new WebSocket(connectionString);

// Main function which handles the connection
// of websocket.
function connect() {
    webSocket.onopen = function open() {
        console.log('WebSockets connection created.');
        // on websocket open, send the START event.
        webSocket.send(JSON.stringify({
            "event": "START",
            "message": ""
        }));
    };

    webSocket.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            connect();
        }, 1000);
    };
    // Sending the info about the room
    webSocket.onmessage = function (e) {
        // On getting the message from the server
        // Do the appropriate steps on each event.
        let data = JSON.parse(e.data);
        data = data["payload"];
        let message = data['message'];
        let event = data["event"];
        //console.log(data);
        switch (event) {
            case "START":
                break;
            case "END":
                toastr.info("Last run was just finished!!!\nYou can save run info by clicking on Accept button.");
                $('#accept_btn').prop('disabled', false);
                set_form_enabled(false);
                break;
            case "RS232":
            //     let values = message.split(">");
            //     if (values.length == 1 || !values)
            //         break;
            //     if (values[1].replace( /[^\d\.]*/g, '').length == 0)
            //         break;
            //     $('#competitor-running-distance').html(parseFloat(values[1].replace( /[^\d\.]*/g, '')));
            //     $('#competitor-running-speed').html(parseFloat(values[3].replace( /[^\d\.]*/g, '')));
            //     let old_weight = parseFloat($('#competitor-running-weight').html());
            //     let new_weight = parseFloat(values[4].replace( /[^\d\.]*/g, ''));
            //     if (old_weight < new_weight)
            //         $('#competitor-running-weight').html(new_weight);
            //     break;
            
            let values = message.split(">");
            if (values.length == 1 || !values) break;
             $('#competitor-running-distance').html(parseFloat(values[1].replace( /[^\d\.]*/g, '')));
            $('#competitor-running-speed').html(parseFloat(values[3].replace(/[^\d\.]*/g, '')));

            let distance = parseFloat(values[1].replace(/[^\d\.]*/g, ''));
            if (distance > 10) { // Ignore weight data for the first 10 meters
         
                let new_weight = parseFloat(values[4].replace(/[^\d\.]*/g, ''));
                let old_weight = parseFloat($('#competitor-running-weight').html());
                if (new_weight > old_weight) { // Ignore weight increases
                    $('#competitor-running-weight').html(new_weight);
                }
            }
            break;
            default:
                console.log("No event")
        }
    };

    if (webSocket.readyState == WebSocket.OPEN) {
        webSocket.onopen();
    }
}

//call the connect function at the start.
connect();

window.classes = [];
window.competitors = [];
window.results = [];

// auto change pull_factor when class_name is changed
function onClassNameChange(selectObject) {
  var selectedClassName = selectObject.value;
  $('#pull_factor').val(window.classes[selectedClassName]);

  // show last 5 runs for current class
  show_last_runs('class', 'class_name', selectedClassName, 5);
}

// auto fill competitor info when competitor_no is inputed
// function onCompetitorNoChange(selectObject) {
//   selectedCompetitorNo = selectObject.value;

//   // if current competitor is already exist
//   if (window.competitors[selectedCompetitorNo]) {
//     $('#competitor_weight').val(window.competitors[selectedCompetitorNo]['weight']);
//     $('#competitor_name').val(window.competitors[selectedCompetitorNo]['competitor_name']);
//     $('#tractor_name').val(window.competitors[selectedCompetitorNo]['tractor_name']);

//     $('#clasS').prop('selectedIndex', parseInt(window.competitors[selectedCompetitorNo]['class_no']));
//     if (window.connection == 'Connected')
//       $('#ready_btn').prop('disabled', false);
//     $('#pull_factor').val(window.competitors[selectedCompetitorNo]['pull_factor']);
//     // $('#clasS').prop('disabled', true);
//     $('#pull_factor').prop('disabled', false);
//   } else {
//     $('#competitor_weight').val('');
//     $('#competitor_name').val('');
//     $('#tractor_name').val('');
//     $('#clasS').prop('selectedIndex', 0);
//     $('#pull_factor').val('');
//     $('#competitor_no').val(selectedCompetitorNo);
//     $('#ready_btn').prop('disabled', true);
//     // $('#clasS').prop('disabled', true);
//     $('#pull_factor').prop('disabled', true);
//     if (selectedCompetitorNo > 0) {
//       $('#clasS').prop('disabled', false);
//       $('#pull_factor').prop('disabled', false);
//     }
//     $('#pull_factor').val(window.classes[$('#clasS').val()]);
//   }

//   // show last 3 runs for current competitor
//   show_last_runs('competitor', 'competitor_no', selectedCompetitorNo, 3);
// }

function onCompetitorNoChange(selectObject) {
  selectedCompetitorNo = selectObject.value;

  // if current competitor is already exist
  if (window.competitors[selectedCompetitorNo]) {
      $('#competitor_weight').val(window.competitors[selectedCompetitorNo]['weight']);
      $('#competitor_name').val(window.competitors[selectedCompetitorNo]['competitor_name']);
      $('#tractor_name').val(window.competitors[selectedCompetitorNo]['tractor_name']);
      $('#clasS').val(window.competitors[selectedCompetitorNo]['class_name']); // Populate class
      $('#pull_factor').val(window.competitors[selectedCompetitorNo]['pull_factor']); // Populate pull factor
      $('#ready_btn').prop('disabled', false);
      $('#pull_factor').prop('disabled', false);
  } else {
      // Reset fields for new competitor
      $('#competitor_weight').val('');
      $('#competitor_name').val('');
      $('#tractor_name').val('');
      $('#clasS').prop('selectedIndex', 0);
      $('#pull_factor').val('');
      $('#competitor_no').val(selectedCompetitorNo);
      $('#ready_btn').prop('disabled', true);
      $('#pull_factor').prop('disabled', true);

      $('#competitor-running-distance').html('');
  }

  // show last 3 runs for current competitor
  show_last_runs('competitor', 'competitor_no', selectedCompetitorNo, 3);
}

function show_last_runs(table_name, by, key, limit) {
  var results_count = window.results.length;
  var matching_count = 0;

  $('#table_for_'+table_name+' tbody').html('');
  for (let i = results_count-1 ; i >= 0 ; i --) {
    let result = window.results[i];
    if (result[by] == key) {
      matching_count ++;
      $('#table_for_'+table_name+' tbody').append('<tr>\n' +
        '                <th scope="row">'+matching_count+'</th>\n' +
        '                <td>'+result["competitor_name"]+'</td>\n' +
        '                <td>'+result["pull_factor"]+'</td>\n' +
        '                <td>'+result["weight"]+'</td>\n' +
        '                <td>'+result["distance"]+'</td>\n' +
        '                <td>'+result["run_date"]+'</td>\n' +
        '                <td>'+result["run_time"]+'</td>\n' +
        '              </tr>');
    }
    if (matching_count == limit)
      break;
  }
  for (let i = matching_count ; i < limit ; i ++)
    $('#table_for_'+table_name+' tbody').append('<tr>\n' +
        '                <th scope="row">'+(i+1)+'</th>\n' +
        '                <td>-----</td>\n' +
        '                <td>-----</td>\n' +
        '                <td>-----</td>\n' +
        '                <td>-----</td>\n' +
        '                <td>-----</td>\n' +
        '                <td>-----</td>\n' +
        '              </tr>');
}

// save a new competitor
function save_competitor() {
    $.ajax({
        url: 'competitor/',
        type: 'POST', // This is the default though, you don't actually need to always mention it
        data: $('form#form1').serialize(),
        success: function(data) {
            if (window.connection == 'Connected')
              $('#ready_btn').prop('disabled', false);
            window.competitors[$('#competitor_no').val()] = {
              'competitor_name': $('#competitor_name').val(),
              'tractor_name': $('#tractor_name').val(),
              'weight': $('#competitor_weight').val(),
              'pull_factor': $('#pull_factor').val(),
              'class_no': $('#clasS').prop('selectedIndex')+1
            };
            window.classes[$('#clasS').val()] = $('#pull_factor').val();
            toastr.success("Competitor data was saved successfully!");
            console.log(data);
        },
        failure: function(data) {
            console.log('Got an error dude');
        }
    });
}

function send_ready_to_server() {
  $('#competitor-running-distance').html(0)
  $('#competitor-running-weight').html(0)
  $('#competitor-running-speed').html(0)
  $.ajax({
        url: 'send_ready/',
        type: 'POST', // This is the default though, you don't actually need to always mention it,
        data: {
            weight: $('#competitor_weight').val(),
            pull_factor: $('#pull_factor').val()
        },
        success: function(data) {
            set_form_enabled(true);
            toastr.info("A run is just started!!!");
            console.log(data);
        },
        failure: function(data) {
            console.log('Got an error dude');
        }
  });
}

function set_form_enabled(flag) {
  $("#competitor_no").prop('disabled', flag);
  $("#competitor_weight").prop('disabled', flag);
  $("#competitor_name").prop('disabled', flag);
  $("#tractor_name").prop('disabled', flag);
  $("#clasS").prop('disabled', flag);
  $("#pull_factor").prop('disabled', flag);
}

function reset_clicked() {
  $('#ready_btn').prop('disabled', true);
  $('#accept_btn').prop('disabled', true);
  // $('#clasS').prop('disabled', true);
  $('#pull_factor').prop('disabled', true);
  $('#competitor-running-distance').html(0)
  $('#competitor-running-weight').html(0)
  $('#competitor-running-speed').html(0)
  set_form_enabled(false);
  $.ajax({
        url: 'reset/',
        type: 'POST', // This is the default though, you don't actually need to always mention it,
        success: function(data) {
            console.log(data);
        },
        failure: function(data) {
            console.log('Got an error dude');
        }
  });
}

function save_result() {
  $.ajax({
        url: 'save_result/',
        type: 'POST', // This is the default though, you don't actually need to always mention it
        data: {
            competitor_no: $('#competitor_no').val(),
            weight: $('#competitor-running-weight').html(),
            distance: $('#competitor-running-distance').html(),
            pull_factor: $('#pull_factor').val()
        },
        success: function(data) {
            toastr.success("Last run was saved successfully!");
            console.log(data);
        },
        failure: function(data) {
            console.log('Got an error dude');
        }
  });
}

function send_msg_to_screen() {
  $.ajax({
        url: 'send_msg_to_screen/',
        type: 'POST', // This is the default though, you don't actually need to always mention it,
        data: {
          msg: $('#msg').val()
        },
        success: function(data) {
            console.log(data);
        },
        failure: function(data) {
            console.log('Got an error dude');
        }
  });
}
