
function subOnQuestion() {
  const jwt = Cookies.get("centrifugo_jwt");
  const url = Cookies.get("centrifugo_url");
  const channel = Cookies.get("centrifugo_channel_question");

  if (url && jwt && channel) {
    
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
    const centrifuge = new Centrifuge(`${protocol}://${url}/connection/websocket`, {
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
      curent_author = document.getElementById('profile-username');
      if (curent_author === null || curent_author.textContent !== ctx.data.answer_author) {
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

function subOnMain() {
    const jwt = Cookies.get("centrifugo_jwt");
    const url = Cookies.get("centrifugo_url");
    const channel = Cookies.get("centrifugo_channel_main");
    if (url && jwt && channel) {
        const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
        const centrifuge = new Centrifuge(`${protocol}://${url}/connection/websocket`, {
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
            alert(ctx.data.message);
        }).on('subscribing', function (ctx) {
            // console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
        }).on('subscribed', function (ctx) {
            // console.log('subscribed', ctx);
        }).on('unsubscribed', function (ctx) {
            // console.log(`unsubscribed: ${ctx.code}, ${ctx.reason}`);
        }).subscribe();
    }
}

function main() {
  subOnQuestion();
  subOnMain();
}

document.addEventListener('DOMContentLoaded', main);
