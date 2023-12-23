if (window.history.replaceState) {
  window.history.replaceState(null, null, window.location.href);
}


function check_daytime(hour) {  
  if (4 <= hour && hour < 12) {
    return 'morning';
  }
  else if (12 <= hour && hour < 16) {
      return 'day';
  }
  else if (16 <= hour && hour < 24) {
      return 'evening';
  }
  else {
      return 'night';
  }
}


document.getElementById('hour').value = new Date().getHours();