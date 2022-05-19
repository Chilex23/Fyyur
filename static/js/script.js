window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};


document.getElementById('delete-btn').addEventListener('click', e => {
  let path = window.location.pathname;
  let id = path.split('/')[2];

  fetch(`/venues/${id}`, {
    method: 'DELETE'
  })
  .then(() => {
    window.location.replace('/')
  })
  .catch(e => {
    console.log(e);
  })
  console.log(id);
})