const container = document.getElementById('top-alert');

// "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDkwNDkxNjcsImlhdCI6MTc0ODQ0NDM2N30.X5sBOJ5yEPC2oH0Zrh13ZZC45SWfwjJ2EW3JJ8JbFbE"

url = Cookies.get("centrifugourl")
token = Cookies.get("jwttoken")
if (url || token) {
  const centrifuge = new Centrifuge(`ws://${url}/connection/websocket`, {
    token: token
  });

  centrifuge.on('connecting', function (ctx) {
    console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
  }).on('connected', function (ctx) {
    console.log(`connected over ${ctx.transport}`);
  }).on('disconnected', function (ctx) {
    console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
  }).connect();

  const sub = centrifuge.newSubscription("channel");

  sub.on('publication', function (ctx) {
    container.innerHTML = ctx.data.value;
    document.title = ctx.data.value;
  }).on('subscribing', function (ctx) {
    console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
  }).on('subscribed', function (ctx) {
    console.log('subscribed', ctx);
  }).on('unsubscribed', function (ctx) {
    console.log(`unsubscribed: ${ctx.code}, ${ctx.reason}`);
  }).subscribe();
}