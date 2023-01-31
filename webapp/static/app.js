var Helpers = {
  postIt: function(data) {
    window.parent.postMessage( data, "*" )
    return false;
  },

  axPost: function( path, data, cb, cbFail = ()=>{} ) {
    $.ajax({
      url:         path,
      method:      "post",
      async:       true,
      dataType:    'json',
      contentType: "application/json",
      data: JSON.stringify(data)
    }).done(cb).fail(cbFail)
  },

  axPut: function( path, data, cb, cbFail = ()=>{} ) {
    $.ajax({
      url:         path,
      method:      "put",
      async:       true,
      dataType:    'json',
      contentType: "application/json",
      data: JSON.stringify(data)
    }).done(cb).fail(cbFail)
  },

  axDelete: function( path, data, cb, cbFail = ()=>{} ) {
    $.ajax({
      url:         path,
      method:      "delete",
      async:       true,
      dataType:    'json',
      contentType: "application/json",
      data: JSON.stringify(data)
    }).done(cb).fail(cbFail)
  },

  axGet: function( path, cb, cbFail = ()=>{} ) {
    $.ajax({
      url:         path,
      method:      "get",
      async:       true,
      dataType:    'json',
      contentType: "application/json",
    }).done(cb).fail(cbFail)
  },

  listenToMsg: function( cb ) {
    window.parent.addEventListener('message', function(event) {
      if ( !event.data || !event.data.type ) return;
      cb(event)
    })
  },

  pstHideUser: function( uuid, dir ) {
    Helpers.postIt( { type: 'hideuser', uuid: uuid, dir: dir } )
  },
};



function tmplt(tmpl_name) {
  return _.template($('#_tmpl_'+tmpl_name).html().replace( "<"+"!--","").replace("--"+">",""));
}


function copyToClipboard(content) {
  var tempInput = document.createElement("input");
  tempInput.style = "position: absolute; left: -1000px; top: -1000px";
  tempInput.value = content;
  document.body.appendChild(tempInput);

  tempInput.select();
  document.execCommand("copy");
  document.body.removeChild(tempInput);
}


function getViewport () {
  const width = Math.max(
    document.documentElement.clientWidth,
    window.innerWidth || 0
  )
  if (width <= 576) return 'xs'
  if (width <= 768) return 'sm'
  if (width <= 992) return 'md'
  if (width <= 1200) return 'lg'
  return 'xl'
}

function millisToMinutesAndSeconds(millis) {
  var minutes = Math.floor(millis / 60000);
  var seconds = ((millis % 60000) / 1000).toFixed(0);
  return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}

function createUUID() {
   return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
   });
}
