!function(l,o,e){l.fn.scrollUp=function(o){l.data(e.body,"scrollUp")||(l.data(e.body,"scrollUp",!0),l.fn.scrollUp.init(o))},l.fn.scrollUp.init=function(r){var s,t=l.fn.scrollUp.settings=l.extend({},l.fn.scrollUp.defaults,r);s=t.scrollTrigger?l(t.scrollTrigger):l("<a/>",{id:t.scrollName,href:"#top"}),t.scrollTitle&&s.attr("title",t.scrollTitle),s.appendTo("body"),t.scrollImg||t.scrollTrigger||s.html(t.scrollText),s.css({display:"none",position:"fixed",zIndex:t.zIndex}),t.activeOverlay&&l("<div/>",{id:t.scrollName+"-active"}).css({position:"absolute",top:t.scrollDistance+"px",width:"100%",borderTop:"1px dotted"+t.activeOverlay,zIndex:t.zIndex}).appendTo("body");var c,n,a,i;switch(t.animation){case"fade":c="fadeIn",n="fadeOut",a=t.animationSpeed;break;case"slide":c="slideDown",n="slideUp",a=t.animationSpeed;break;default:c="show",n="hide",a=0}i="top"===t.scrollFrom?t.scrollDistance:l(e).height()-l(o).height()-t.scrollDistance;var d=!1;scrollEvent=l(o).scroll(function(){l(o).scrollTop()>i?d||(s[c](a),d=!0):d&&(s[n](a),d=!1)});var p;t.scrollTarget?"number"==typeof t.scrollTarget?p=t.scrollTarget:"string"==typeof t.scrollTarget&&(p=Math.floor(l(t.scrollTarget).offset().top)):p=0,s.click(function(o){o.preventDefault(),l("html, body").animate({scrollTop:p},t.scrollSpeed,t.easingType)})},l.fn.scrollUp.defaults={scrollName:"scrollUp",scrollDistance:300,scrollFrom:"top",scrollSpeed:300,easingType:"linear",animation:"fade",animationSpeed:200,scrollTrigger:!1,scrollTarget:!1,scrollText:"Scroll to top",scrollTitle:!1,scrollImg:!1,activeOverlay:!1,zIndex:2147483647},l.fn.scrollUp.destroy=function(r){l.removeData(e.body,"scrollUp"),l("#"+l.fn.scrollUp.settings.scrollName).remove(),l("#"+l.fn.scrollUp.settings.scrollName+"-active").remove(),l.fn.jquery.split(".")[1]>=7?l(o).off("scroll",r):l(o).unbind("scroll",r)},l.scrollUp=l.fn.scrollUp}(jQuery,window,document);