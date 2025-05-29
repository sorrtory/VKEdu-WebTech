
function main() {

  const jwt = Cookies.get("centrifugo_jwt");
  const url = Cookies.get("centrifugo_url");
  const channel = Cookies.get("centrifugo_channel");

  if (url && jwt && channel) {
    const centrifuge = new Centrifuge(`ws://${url}/connection/websocket`, {
      token: jwt
    });

    centrifuge.on('connecting', function (ctx) {
      // console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
    }).on('connected', function (ctx) {
      // console.log(`connected over ${ctx.transport}`);
    }).on('disconnected', function (ctx) {
      // console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
    }).connect();

    const sub = centrifuge.newSubscription(channel);

    sub.on('publication', function (ctx) {
      curent_author = document.getElementById('profile-username').textContent;
      if (curent_author !== ctx.data.answer_author) {
        document.getElementById('top-alert-link').href = ctx.data.link_to_new_answer;
        const words = ctx.data.answer_content.split(' ');
        const truncated = words.slice(0, 10).join(' ') + (words.length > 10 ? '...' : '');
        // From the base.html
        showAlert(`${ctx.data.answer_author} has added new answer to this question: ${truncated}`);
      }
    }).on('subscribing', function (ctx) {
      // console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
    }).on('subscribed', function (ctx) {
      // console.log('subscribed', ctx);
    }).on('unsubscribed', function (ctx) {
      // console.log(`unsubscribed: ${ctx.code}, ${ctx.reason}`);
    }).subscribe();
  }
}

document.addEventListener('DOMContentLoaded', main);
