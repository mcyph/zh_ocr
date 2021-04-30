function escapeHTML(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}


function isScrolledIntoView(el) {
    var rect = el.getBoundingClientRect();
    var elemTop = rect.top;
    var elemBottom = rect.bottom;

    // Only completely visible elements return true:
    var isVisible = elemTop < window.innerHeight && elemBottom >= 0
    // Partially visible elements return true:
    //isVisible = elemTop < window.innerHeight && elemBottom >= 0;
    return isVisible;
}

function jsonToQueryString(json) {
    return '?' +
        Object.keys(json).map(function(key) {
            return encodeURIComponent(key) + '=' +
                encodeURIComponent(json[key]);
        }).join('&');
}



function ImageInst(image_name, LDTSV) {
    this.image_name = image_name;
    this.elm = document.createElement('div');
    document.body.appendChild(this.elm);
    this.elm.className = 'image_cont';
    this.src = '/img/10 level chinese 7 intensive/png_out/'+image_name+'.png';

    this.width = (1920/2); // HACK!
    this.height = (2715/2); // HACK!
    this.elm.style.width = this.width+'px'
    this.elm.style.height = this.height+'px'
    //console.log(this.elm.style.backgroundImage)

    this.LDTSV = LDTSV;


}

ImageInst.prototype = {
    addElements: function() {
        var that = this;

        this.LDTSV.forEach(function(DTSV) {
            if (DTSV['text_trad'].trim()) {
                // Only add if there's text to add!!!
                that.addElement(DTSV);
            }
        });
    },

    removeElements: function() {
        var that = this;
        this.onMouseOut();

        this.LDTSV.forEach(function(DTSV) {
            if (!DTSV['div']) {
                return;
            }
            that.elm.removeChild(DTSV['div']);
            delete DTSV['div'];
        });
    },

    addElement: function(DTSV) {
        //console.log(DTSV)
        var div = document.createElement('div'),
            s = div.style;

        div.className = 'text_cont';
        s.left = DTSV['left']+'px';
        s.top = DTSV['top']+'px';
        s.height = DTSV['height']+'px';
        s.width = DTSV['width']+'px';
        s.opacity = '0.'+s.confidence;

        div.innerHTML = '<span>'+escapeHTML(String(DTSV['text_trad']))+'</span>';
        this.elm.appendChild(div);
        div.setAttribute('contenteditable', true);
        DTSV['div'] = div;

        this.adjustFont(div, DTSV['width']);

        var that = this;
        div.onkeydown = onkeypress = function() {
            setTimeout(function() {
                that.onChange(DTSV);
            }, 0);
        }
        div.onmouseover = function() {
            that.onMouseOver(DTSV);
        }
        div.onmouseout = function() {
            that.onMouseOut(DTSV);
        }
    },

    onMouseOver: function(DTSV) {
        this.onMouseOut();

        if (!this.img) {
            // Create the additional image on-demand,
            // to save memory until it's needed
            this.img = document.createElement('img');
            this.img.className = 'clip_img';
            this.img.src = this.src;
            this.elm.appendChild(this.img);
        }

        // values are from-top, from-right, from-bottom, from-left
        this.img.style.clipPath = (
            'inset('+
            DTSV['top']+'px '+
            (this.width-DTSV['width']-DTSV['left'])+'px '+
            (this.height-DTSV['height']-DTSV['top'])+'px '+
            DTSV['left']+'px'+
            ')'
        );

        this.img.style.left = '0px';
        this.img.style.top = -DTSV['height']-10+'px';
        this.img.style.display = 'block';

        // Show the simplified text
        this.simpPop = document.createElement('div');
        this.simpPop.className = 'simp_pop';
        this.simpPop.style.top = DTSV['top']+DTSV['height']+10+'px';
        this.simpPop.style.left = DTSV['left']+'px';
        this.simpPop.style.fontSize = DTSV['div'].style.fontSize;
        this.simpPop.innerHTML = escapeHTML(DTSV['text']);
        this.simpPop.style.width = DTSV['width']+'px';
        this.elm.appendChild(this.simpPop);

    },

    onMouseOut: function(DTSV) {
        if (this.img) {
            this.img.style.display = 'none';
        }
        if (this.simpPop) {
            this.elm.removeChild(this.simpPop);
            this.simpPop = null;
        }
    },

    onChange: function(DTSV) {
        // TODO: Send changes via ajax!
        var hash = DTSV['hash'],
            text = DTSV[FIXME].innerHTML;
    },

    adjustFont: function(div, width) {
        // Make font as large as possible x-wise, without clipping
        var fontSize = 10.0,
            span = div.firstChild,
            x = 0;

        while (true) {
            // First do bigger steps, to minimise CPU cycles
            span.style.fontSize = fontSize+'px';
            //console.log(span.offsetWidth+' '+width)
            if (span.offsetWidth >= width) {
                span.style.fontSize = (fontSize-1.0)+'px';
                break;
            }
            else if (x > 20) {
                // Prevent an infinite loop!
                span.style.fontSize = '10px'
                break;
            }
            fontSize += 5.0;
            x += 1;
        }

        x = 0;
        while (true) {
            // Then go back with smaller steps
            fontSize -= 1.0;
            span.style.fontSize = fontSize+'px';
            if (span.offsetWidth <= width) {;
                break;
            }
            else if (x > 20) {
                // Prevent an infinite loop!
                span.style.fontSize = '10px'
                break;
            }
            x += 1;
        }
    },

    onScroll: function(docViewTop, docViewBottom) {
        var inView = isScrolledIntoView(this.elm);
        //console.log(topY+' '+bottomY+' '+inView);

        if (inView && !this.imgShown) {
            this.imgShown = true;
            this.addElements();
            this.elm.style.backgroundImage = 'url("'+this.src+'")' // HACK HACK!
        }
        else if (!inView && this.imgShown) {
            this.imgShown = false;
            this.removeElements();
            this.elm.style.backgroundImage = 'none';
        }
    },

    onChange: function(DTSV) {
        var newText = DTSV['div'].innerText || DTSV['div'].textContent;

        var xhttp = new XMLHttpRequest();
        xhttp.open("GET", "set_exception"+jsonToQueryString({
            hash: DTSV['hash'],
            orig_text: DTSV['orig_text'],
            new_text: newText
        }), true);
        xhttp.send();

        // Update the text, so it will be displayed
        // when scrolled away from, then back to again
        DTSV['text_trad'] = newText;
    }
}


function Images(LImages) {
    LImageInsts = this.LImageInsts = [];

    LImages.forEach(function(L) {
        LImageInsts.push(new ImageInst(L[0], L[1]));
    })

    var that = this;
    window.onscroll = function() {
        that.onscroll();
    }

    this.onscroll()
}

Images.prototype = {
    onscroll: function() {
        // TODO: Only render on-demand!!!


        var docViewTop = window.scrollY,
            docViewBottom = docViewTop + window.innerHeight;

        //console.log("SCROLL: "+docViewBottom+" "+docViewTop)

        var that = this;
        this.LImageInsts.forEach(function(inst) {
            inst.onScroll(docViewTop, docViewBottom);
        })
    }
}

