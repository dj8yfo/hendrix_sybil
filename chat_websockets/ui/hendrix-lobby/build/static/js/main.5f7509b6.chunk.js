(this["webpackJsonphendrix-lobby"]=this["webpackJsonphendrix-lobby"]||[]).push([[0],{19:function(e,t,n){e.exports=n(38)},30:function(e,t,n){},31:function(e,t,n){},32:function(e,t,n){},33:function(e,t,n){},34:function(e,t,n){},35:function(e,t,n){},36:function(e,t,n){},37:function(e,t,n){},38:function(e,t,n){"use strict";n.r(t);var a=n(0),o=n.n(a),r=n(10),s=n.n(r),c=n(2),i=n(3),l=n(5),u=n(4),d=n(6),p=n(7);n(30);function m(e,t){return t===e.pendingMsgToken?"":e.pendingMsgToken}function g(){return!!/Mobile|Android|webOS|iPhone|iPad|iPod|BlackBerry|BB|PlayBook|IEMobile|Windows Phone|Kindle|Silk|Opera Mini/i.test(navigator.userAgent)}function O(e){if(null==e)return 0;var t=e>-1?e+1:null;return t>0?t:0}var f,h=function(e){function t(){return Object(c.a)(this,t),Object(l.a)(this,Object(u.a)(t).apply(this,arguments))}return Object(d.a)(t,e),Object(i.a)(t,[{key:"computeTooltip",value:function(){var e=this.props.proto;return e.pendingMsgToken||e.unhandledWsMessage}},{key:"render",value:function(){var e=this.props,t=e.connection,n=e.messages,a=e.statusLast,r=O(n.lastMessage),s=g()?"80%":"100%";return o.a.createElement("div",{className:"stats",style:{fontSize:s}},o.a.createElement("p",{"data-tooltip":JSON.stringify(a.info),"data-tooltip-location":"right"},"status:"," ",t.authenticating?"uploading...":t.connected?"connected":t.connecting?"connecting...":"disconnected"),o.a.createElement("div",null,"sleeve:"," ",o.a.createElement("text",{"data-tooltip":"".concat("You've been resleeved to a stock option: ").concat(n.nym,".\n").concat("\nRegular customers of Hendrix are offered a wide selection of bespoke sleeves."),"data-tooltip-location":"right"},n.nym)),o.a.createElement("p",null," room: ",n.room),o.a.createElement("p",null," prev messages: ",r||"None"," "),o.a.createElement("div",null,o.a.createElement("div",{className:"block-msg"},o.a.createElement("text",{"data-tooltip":this.computeTooltip(),"data-tooltip-location":"right"},"\u03c3 tip \u03c3"))))}}]),t}(o.a.Component),y=Object(p.b)((function(e){return{connection:e.connection,messages:e.messages,proto:e.proto,statusLast:e.statusLast}}))(h),b=(n(31),n(9)),v=(n(32),n(14)),T=n.n(v);f=g()?260:600;var _=function(e){function t(){return Object(c.a)(this,t),Object(l.a)(this,Object(u.a)(t).apply(this,arguments))}return Object(d.a)(t,e),Object(i.a)(t,[{key:"renderTxtDiv",value:function(e,t){var n={width:"".concat(t,"px"),overflowWrap:"break-word"};return o.a.createElement("div",{className:"txt-content",style:n,dangerouslySetInnerHTML:{__html:e}})}},{key:"render",value:function(){var e=this.props,t=e.value,n=e.color,a="hendrix"===t.from_nym,r=function(e){var t=new Date(1e3*e),n=t.getFullYear(),a=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][t.getMonth()],o=t.getDate(),r=t.getHours();r=r<10?"0"+r:r;var s=t.getMinutes();s=s<10?"0"+s:s;var c=t.getSeconds();return[o+" "+a+" "+n+" ",r+":"+s+":"+(c=c<10?"0"+c:c)]}(t.date_created),s=r[0],c=r[1],i=T()("bg-border-blur"),l=T()({"bg-image-blur":!a},"image-frame","block-msg");return o.a.createElement("div",{className:"entry-msg",ref:this.props.inputRef},o.a.createElement("div",{className:l},o.a.createElement("div",{className:i},a?o.a.createElement("img",{src:"./hendrix.gif",alt:"hendrix",className:"immg",width:68,height:90}):o.a.createElement("img",{src:"./djunxiety.webp",alt:"djunxiety",className:"immg",width:68,height:58}))),o.a.createElement("div",{className:"block-msg msg-header"},a?null:o.a.createElement("div",{className:"nym-content"},o.a.createElement("font",{color:n},"".concat(t.from_nym))),o.a.createElement("div",{className:"date-msg"},s),o.a.createElement("div",{className:"date-msg"},c)),o.a.createElement("div",{className:"block-msg"},o.a.createElement("div",{className:"content"},this.renderTxtDiv(t.content,f))))}}]),t}(o.a.Component),E=n(39);function S(e,t){return function(n){var a=Object(E.a)(),o={action:"select_room",destination_room:t,token:a};n({type:"PROTO_SELROOM_STARTED",payload:a}),e.send(JSON.stringify(o))}}function k(e,t){return function(n){var a;try{a=JSON.parse(n.data)}catch(o){return void e({type:"PROTO_UNKNOWN",payload:n.data})}switch(e({type:"PROTO_GENERIC",payload:a}),a.msg.action){case"authenticate":!function(e,t,n){switch(e.status){case"success":t({type:"PROTO_AUTH_SUCCESS",payload:{token:e.msg.token,nym:e.msg.from_nym}}),S(n,"Lobby")(t);break;case"error":t({type:"PROTO_AUTH_FAIL",payload:{token:e.msg.token}});break;default:;}}(a,e,t);break;case"select_room":!function(e,t){switch(e.status){case"success":t({type:"PROTO_SELROOM_SUCCESS",payload:{token:e.msg.token,room:e.msg.room,perPage:e.msg.page,lastMessage:e.msg.last_message}});break;case"error":t({type:"PROTO_SELROOM_FAIL",payload:{token:e.msg.token}});break;default:;}}(a,e);break;case"send_message":!function(e,t){switch(e.status){case"success":t({type:"PROTO_MSG_RCVD",payload:{content:e.msg.content,date_created:e.msg.date_created,from_nym:e.msg.from_nym,token:e.msg.token,viewed:!1}}),setTimeout((function(){t({type:"PROTO_MSG_CLEAR_NOTIFY"})}),1e3);break;case"error":t({type:"PROTO_MSG_FAIL",payload:{token:e.msg.token}});break;default:;}}(a,e);break;case"history_retrieve":!function(e,t){switch(e.status){case"success":var n=e.msg.result.map((function(e){return{content:e.content,date_created:e.date_created,from_nym:e.from_nym,viewed:!0}}));t({type:"PROTO_HISTORY_SUCCESS",payload:{token:e.msg.token,room:e.msg.room,history:n}});break;case"error":t({type:"PROTO_HISTORY_FAIL",payload:e.msg.token});break;default:;}}(a,e);break;default:e({type:"PROTO_UNKNOWN",payload:n.data})}}}var R=null;function N(){R.close()}n(33);var j=f+200,C=g?500:600,M=function(e){function t(e){var n;return Object(c.a)(this,t),(n=Object(l.a)(this,Object(u.a)(t).call(this,e))).state={lastScrollTop:null,maxScroll:null,colors:{},childrefs:null,messages:[]},n.btnClickHandler=function(e){var t=n.props.messages,a=t.lastMessage,o=t.room;n.props.historyRetrieve(a,o)},n.scrollTopHandler=function(){var e=n.viewPort.current.scrollTop,t=n.viewPort.current.offsetHeight;if(null!=n.state.lastScrollTop){if(e>n.state.lastScrollTop)n.checkViewedMessaged(e+t);else if(e<10){var a=n.props.messages,o=a.lastMessage,r=a.room,s=a.pendingMsgToken;if(n.historyDisabled(s,r,o)||n.props.historyRetrieve(o,r),O(o))return void(n.viewPort.current.scrollTop=n.state.lastScrollTop)}n.state.lastScrollTop=e<=0?0:e}else n.state.lastScrollTop=e<=0?0:e},n.viewPort=o.a.createRef(),n}return Object(d.a)(t,e),Object(i.a)(t,[{key:"historyDisabled",value:function(e,t,n){return Boolean(e)||!Boolean(t)||n<0}},{key:"renderTemplate",value:function(e){var t=this;return this.state.messages=Object(b.a)(this.props.messages.messages),this.state.childrefs=[],e.map((function(e,n){void 0===t.state.colors[e.from_nym]&&(t.state.colors[e.from_nym]=function(){for(var e="#",t=0;t<6;t++)e+="0123456789ABCDEF"[Math.floor(16*Math.random())];return e}());var a=t.state.colors[e.from_nym],r=String(e.date_created)+n;return o.a.createElement(_,{key:r,value:e,color:a,inputRef:function(e){t.state.childrefs.push(e)}})}))}},{key:"checkViewedMessaged",value:function(e){var t=this,n=!1;this.state.childrefs.filter((function(e){return null!=e})).forEach((function(a,o){var r=a.offsetHeight+a.offsetTop;e>=r-5&&(t.state.messages[o].viewed||(n=!0),t.state.messages[o].viewed=!0)})),n&&this.props.indicateNewMessages(this.state.messages)}},{key:"componentDidUpdate",value:function(){var e=this.viewPort.current.scrollTop,t=this.viewPort.current.offsetHeight;this.checkViewedMessaged(e+t)}},{key:"render",value:function(){var e=this.props.messages,t=e.messages,n=e.pendingMsgToken,a=e.room,r=e.lastMessage,s=e.closedscr,c=e.notifyFlag,i=this.historyDisabled(n,a,r),l=c?"#999999":"#444444",u=t.filter((function(e){return!1===e.viewed})).length>0,d=3*j/4;return o.a.createElement("div",{className:"msgs"},o.a.createElement("button",{key:"history-btn-key",className:"shadowbtn btn",style:{height:"20px",width:"100%"},onClick:this.btnClickHandler,disabled:i}," ","hist"),o.a.createElement("div",{className:"viewport",id:"containerElement",ref:this.viewPort,onScroll:this.scrollTopHandler,style:{position:"relative",height:"550px",width:"".concat(j,"px"),overflow:"scroll",overflowX:"hidden",scrollbarWidth:"thick",scrollbarColor:"".concat(l," #000000"),marginBottom:"10px",border:"1px",borderRight:"0px",borderLeft:"0px",borderBottom:"1px",borderStyle:"solid",borderColor:"#444444",alignItems:"center"}},s?o.a.createElement("div",{className:"centered"},o.a.createElement("img",{src:"./ecorp.gif",alt:"hendrix",width:C,height:C})):o.a.createElement(o.a.Fragment,null,this.renderTemplate(t))),u?o.a.createElement("div",{className:"arrow",style:{left:"".concat(d,"px"),top:"540px"}},o.a.createElement("img",{alt:"scroll-down",width:30,height:30,src:"./arrow.png"})):null)}}]),t}(o.a.Component),w=Object(p.b)((function(e){return{messages:e.messages}}),(function(e){return{historyRetrieve:function(t,n){return e(function(e,t,n){var a=Object(E.a)(),o={action:"history_retrieve",token:a,room:t,last_message:e};return n.send(JSON.stringify(o)),{type:"PROTO_HISTORY_GET_STARTED",payload:a}}(t,n,R))},indicateNewMessages:function(t){return e({type:"CHANGED_NEW_MESSAGES_INDICATOR",payload:t})}}}))(M);var P=function(e){function t(e){var n;return Object(c.a)(this,t),(n=Object(l.a)(this,Object(u.a)(t).call(this,e))).commonHandler=function(){if(n.input.current.value){var e,t=n.input.current.value;if(n.input.current.value="",t.startsWith("/menu"))n.props.query();else if(t.startsWith("/rent-lavatory-room")){var a=t.split(" ");if(!(2===a.length&&(e=a[1],"string"===typeof e||e instanceof String)&&a[1].length>0))return;var o=a[1];n.props.changeRoom(o)}else n.props.sender(t)}},n.keyPrsHandler=function(e){return 13!==e.keyCode&&13!==e.which||(n.commonHandler(),!1)},n.btnClickHandler=function(e){e.preventDefault(),n.commonHandler()},n.input=o.a.createRef(),n}return Object(d.a)(t,e),Object(i.a)(t,[{key:"render",value:function(){var e=this.props.disabled;return o.a.createElement("div",{className:"table",style:{width:j}},o.a.createElement("div",{className:"group-header"},o.a.createElement("div",{className:"pref-input-container cell",style:{width:j-110}},o.a.createElement("input",{id:"unique_say",className:"prefixed-input",type:"text",style:{width:j-150},onKeyPress:this.keyPrsHandler,disabled:e,ref:this.input}),o.a.createElement("span",{className:"inside-prefixed-input",style:{marginLeft:-1*(j-135)}},"$")),o.a.createElement("div",{className:"cell"},o.a.createElement("button",{className:"shadowbtn big-btn",onClick:this.btnClickHandler,disabled:e}," ","say"))))}}]),t}(o.a.Component),A=(n(34),function(e){function t(){return Object(c.a)(this,t),Object(l.a)(this,Object(u.a)(t).apply(this,arguments))}return Object(d.a)(t,e),Object(i.a)(t,[{key:"render",value:function(){var e=this.props,t=e.proto,n=e.sendMessage,a=e.sendQueryMenu,r=e.initSelectroom,s=Boolean(t.pendingMsgToken)||!Boolean(t.room),c="Lobby"===t.room?a:function(){};return o.a.createElement("div",{className:"chat-proto"},o.a.createElement(P,{sender:n,query:c,changeRoom:r,disabled:s}))}}]),t}(o.a.Component)),H=Object(p.b)((function(e){return{proto:e.proto}}),(function(e){return{sendMessage:function(t){return e(function(e,t){var n=Object(E.a)(),a={action:"send_message",token:n,content:e};return t.send(JSON.stringify(a)),{type:"PROTO_SEND_MSG",payload:n}}(t,R))},sendQueryMenu:function(){return e(function(e){var t=Object(E.a)(),n={action:"query",token:t,query_name:"/menu",parameters:{}};return e.send(JSON.stringify(n)),{type:"PROTO_SEND_MSG",payload:t}}(R))},initSelectroom:function(t){return e(S(R,t))}}}))(A),D=(n(35),function(e){function t(){return Object(c.a)(this,t),Object(l.a)(this,Object(u.a)(t).apply(this,arguments))}return Object(d.a)(t,e),Object(i.a)(t,[{key:"render",value:function(){var e=this.props,t=e.connection,n=e.initConnect,a=e.initAuthenticate;return o.a.createElement("div",{className:"cell",style:{paddingRight:"20px"}},o.a.createElement("button",{className:"darkbtn btn",disabled:t.connected||t.connecting,onClick:n},"enter lobby"),o.a.createElement("button",{className:"darkbtn btn",disabled:t.authenticated||t.authenticating||!t.connected||t.connecting,onClick:a},"upload consciousness"),o.a.createElement("button",{className:"darkbtn btn",disabled:!(t.connected||t.connecting),onClick:N},"leave hendrix"))}}]),t}(o.a.Component)),L=Object(p.b)((function(e){return{connection:e.connection}}),(function(e){return{initConnect:function(){return e((function(e){e({type:"CONNECT_TO_WS_REQUEST"}),(R=new WebSocket("wss://".concat(window.location.host,"/ws"))).onopen=function(t){e({type:"CONNECT_TO_WS_ESTABLISHED",payload:t})},R.onerror=function(t){e({type:"CONNECT_TO_WS_ERRORED",payload:t})},R.onclose=function(t){e({type:"CONNECT_TO_WS_CLOSED",payload:t})},R.onmessage=k(e,R)}))},initAuthenticate:function(){return e((t=R,function(e){var n=Object(E.a)(),a={action:"authenticate",token:n};e({type:"PROTO_AUTH_STARTED",payload:n}),t.send(JSON.stringify(a))}));var t}}}))(D),W=(n(36),function(e){function t(){return Object(c.a)(this,t),Object(l.a)(this,Object(u.a)(t).apply(this,arguments))}return Object(d.a)(t,e),Object(i.a)(t,[{key:"render",value:function(){return o.a.createElement("div",{className:g()?"not-centered":"centered"},o.a.createElement("div",null,o.a.createElement("div",{className:"table",style:{width:j}},o.a.createElement("div",{className:"group-header greyish"},o.a.createElement("div",{className:"cell stats"},o.a.createElement(y,null)),o.a.createElement("div",{className:"cell"},o.a.createElement("div",{className:"App-header"},"Hendrix")),o.a.createElement(L,null))),o.a.createElement(w,null),o.a.createElement(H,null)))}}]),t}(o.a.Component)),x=n(8),I=n(1),U={connected:!1,connecting:!1,authenticated:!1,authenticating:!1,error:""};var F={unhandledWsMessage:null,nym:null,pendingMsgToken:"",room:null,perPage:null,lastMessage:null};var G={messages:[],nym:null,lastMessage:null,room:null,perPage:null,pendingMsgToken:"",closedscr:null,notifyFlag:null};var B={info:{}};var Y=Object(x.c)({connection:function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:U,t=arguments.length>1?arguments[1]:void 0;switch(t.type){case"CONNECT_TO_WS_REQUEST":return Object(I.a)({},e,{connecting:!0});case"CONNECT_TO_WS_ERRORED":return Object(I.a)({},e,{connecting:!1,error:t.payload.type});case"CONNECT_TO_WS_ESTABLISHED":return Object(I.a)({},e,{connecting:!1,connected:!0});case"CONNECT_TO_WS_CLOSED":return Object(I.a)({},e,{connecting:!1,connected:!1,authenticated:!1});case"PROTO_AUTH_STARTED":return Object(I.a)({},e,{authenticating:!0});case"PROTO_AUTH_SUCCESS":return Object(I.a)({},e,{authenticated:!0,authenticating:!1});case"PROTO_AUTH_FAIL":return Object(I.a)({},e,{authenticating:!1});default:return e}},proto:function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:F,t=arguments.length>1?arguments[1]:void 0;switch(t.type){case"CONNECT_TO_WS_CLOSED":return Object(I.a)({},e,{pendingMsgToken:"",nym:null,room:null,perPage:null,lastMessage:null,unhandledWsMessage:"left Hendrix"});case"CONNECT_TO_WS_ESTABLISHED":return Object(I.a)({},e,{unhandledWsMessage:"shall set foot on Hendrix threshold"});case"PROTO_AUTH_STARTED":return Object(I.a)({},e,{pendingMsgToken:t.payload});case"PROTO_AUTH_SUCCESS":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload.token),nym:t.payload.nym,unhandledWsMessage:"consciousness uploaded"});case"PROTO_AUTH_FAIL":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload.token)});case"PROTO_SELROOM_STARTED":return Object(I.a)({},e,{pendingMsgToken:t.payload});case"PROTO_SELROOM_SUCCESS":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload.token),room:t.payload.room,perPage:t.payload.perPage,lastMessage:t.payload.lastMessage});case"PROTO_SELROOM_FAIL":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload.token)});case"PROTO_SEND_MSG":return Object(I.a)({},e,{pendingMsgToken:t.payload});case"PROTO_MSG_RCVD":case"PROTO_MSG_FAIL":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload.token)});case"PROTO_HISTORY_GET_STARTED":return Object(I.a)({},e,{pendingMsgToken:t.payload});case"PROTO_HISTORY_FAIL":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload)});case"PROTO_HISTORY_SUCCESS":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload.token)});case"PROTO_UNKNOWN":return Object(I.a)({},e,{unhandledWsMessage:t.payload});default:return e}},messages:function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:G,t=arguments.length>1?arguments[1]:void 0;switch(t.type){case"CONNECT_TO_WS_CLOSED":return Object(I.a)({},e,{messages:[],pendingMsgToken:"",lastMessage:null,room:null,perPage:null,nym:null,closedscr:!0});case"PROTO_AUTH_SUCCESS":return Object(I.a)({},e,{nym:t.payload.nym,closedscr:!1});case"PROTO_SELROOM_SUCCESS":return Object(I.a)({},e,{messages:[],lastMessage:t.payload.lastMessage,room:t.payload.room,perPage:t.payload.perPage});case"PROTO_MSG_RCVD":return Object(I.a)({},e,{messages:[].concat(Object(b.a)(e.messages),[t.payload]),notifyFlag:!0});case"PROTO_MSG_CLEAR_NOTIFY":return Object(I.a)({},e,{notifyFlag:!1});case"PROTO_HISTORY_GET_STARTED":return Object(I.a)({},e,{pendingMsgToken:t.payload});case"PROTO_HISTORY_FAIL":return Object(I.a)({},e,{pendingMsgToken:m(e,t.payload)});case"PROTO_HISTORY_SUCCESS":return e.room===t.payload.room?Object(I.a)({},e,{lastMessage:e.lastMessage-e.perPage,messages:[].concat(Object(b.a)(t.payload.history),Object(b.a)(e.messages)),pendingMsgToken:m(e,t.payload.token)}):Object(I.a)({},e,{pendingMsgToken:m(e,t.payload.token)});case"CHANGED_NEW_MESSAGES_INDICATOR":return Object(I.a)({},e,{messages:t.payload});default:return e}},statusLast:function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:B,t=arguments.length>1?arguments[1]:void 0;switch(t.type){case"PROTO_GENERIC":return Object(I.a)({},e,{info:t.payload});case"CONNECT_TO_WS_CLOSED":return Object(I.a)({},e,{info:{}});default:return e}}}),J=n(17),V=Object(x.d)(Y,Object(x.a)(J.a)),q=Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));function K(e,t){navigator.serviceWorker.register(e).then((function(e){e.onupdatefound=function(){var n=e.installing;null!=n&&(n.onstatechange=function(){"installed"===n.state&&(navigator.serviceWorker.controller?(console.log("New content is available and will be used when all tabs for this page are closed. See https://bit.ly/CRA-PWA."),t&&t.onUpdate&&t.onUpdate(e)):(console.log("Content is cached for offline use."),t&&t.onSuccess&&t.onSuccess(e)))})}})).catch((function(e){console.error("Error during service worker registration:",e)}))}n(37);s.a.render(o.a.createElement(p.a,{store:V},o.a.createElement(W,null)),document.getElementById("root")),function(e){if("serviceWorker"in navigator){if(new URL("",window.location.href).origin!==window.location.origin)return;window.addEventListener("load",(function(){var t="".concat("","/service-worker.js");q?(!function(e,t){fetch(e,{headers:{"Service-Worker":"script"}}).then((function(n){var a=n.headers.get("content-type");404===n.status||null!=a&&-1===a.indexOf("javascript")?navigator.serviceWorker.ready.then((function(e){e.unregister().then((function(){window.location.reload()}))})):K(e,t)})).catch((function(){console.log("No internet connection found. App is running in offline mode.")}))}(t,e),navigator.serviceWorker.ready.then((function(){console.log("This web app is being served cache-first by a service worker. To learn more, visit https://bit.ly/CRA-PWA")}))):K(t,e)}))}}()}},[[19,1,2]]]);
//# sourceMappingURL=main.5f7509b6.chunk.js.map