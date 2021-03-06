/*
	joystick - 2.0.0
	https://github.com/jquery-element/joystick
*/

(function( $ ) {

    "use strict";
    
    var
        joystickCurrent,
        jqWindow = $( window ),
        onDesktop = areWeOnDesktop()
    ;
    
    function areWeOnDesktop() {
        try {
            document.createEvent( "TouchEvent" );
            return false;
        } catch ( e ) {
            return true;
        }
    }
    
    function winMove( e ) {
        var joy, t, i = 0;
        if ( joystickCurrent ) {
            e.preventDefault();
            if ( onDesktop ) {
                joystickCurrent.move( e.pageX, e.pageY );
            } else {
                e = e.originalEvent.changedTouches;
                while ( t = e[ i++ ] ) {
                    if ( joy = joystickCurrent[ t.identifier ] ) {
                        joy.move( t.pageX, t.pageY );
                    }
                }
            }
        }
    }
    
    function winRelease( e ) {
        var joy, t, i = 0;
        if ( joystickCurrent ) {
            e.preventDefault();
            if ( onDesktop ) {
                joystickCurrent.release();
                joystickCurrent = null;
            } else {
                e = e.originalEvent.changedTouches;
                while ( t = e[ i++ ] ) {
                    if ( joy = joystickCurrent[ t.identifier ] ) {
                        joy.release();
                        delete joystickCurrent[ t.identifier ];
                    }
                }
                if ( $.isEmptyObject( joystickCurrent ) ) {
                    joystickCurrent = null;
                }
            }
        }
    }

    var request=(command,coordX,coordY,params={})=>{
        //console.log({action:'sendCommand',command:command,params:params})   
        console.log("coordX : " + coordX)
        console.log("coordY : " + coordY)
        var arg = '';
        if(coordX < 0 && coordY > -10 && coordY < 10){
            arg += 'L';
        }
        else if(coordX > 0 && coordY > -10 && coordY < 10){
            arg += 'R';
        }

        else if(coordY < 0 && coordX > -10 && coordX < 10){
            arg += 'U';
        }

        else if(coordY > 0 && coordX > -10 && coordX < 10){
            arg += 'D';
        }

        else if(coordX < -10 && coordY < -10){
            arg += 'LU'
        }
        else if(coordX > 10 && coordY < -10){
            arg += 'RU'
        }
        else if(coordX < -10 && coordY > 10){
            arg += 'LD'
        }
        else if(coordX > 10 && coordY > 10){
            arg += 'RD'
        }

        else if(coordY == 0 && coordX == 0){
            arg += 'S'
        }
        
        params['command'] = command
        params['direction'] = arg;
        $.post("/api/command/",params).done((json)=>{
            console.log({action:'sendCommand',json:json})
        },'json')
    }

    var cam_request=(command,coordX,coordY,params={})=>{
        //console.log({action:'sendCommand',command:command,params:params})   
        console.log("coordX : " + coordX)
        console.log("coordY : " + coordY)
        var arg = '';
        if(coordX < 0 && coordY > -10 && coordY < 10){
            arg += 'W';
        }
        else if(coordX > 0 && coordY > -10 && coordY < 10){
            arg += 'E';
        }

        else if(coordY < 0 && coordX > -10 && coordX < 10){
            arg += 'N';
        }

        else if(coordY > 0 && coordX > -10 && coordX < 10){
            arg += 'S';
        }

        else if(coordX < -10 && coordY < -10){
            arg += 'NW'
        }
        else if(coordX > 10 && coordY < -10){
            arg += 'NE'
        }
        else if(coordX < -10 && coordY > 10){
            arg += 'SW'
        }
        else if(coordX > 10 && coordY > 10){
            arg += 'SE'
        }

        else if(coordY == 0 && coordX == 0){
            arg += 'C'
        }
        
        params['command'] = command
        params['direction'] = arg;
        $.post("/api/command/",params).done((json)=>{
            console.log({action:'sendCommand',json:json})
        },'json')
    }

    jqWindow
        .on( onDesktop ? "mousemove" : "touchmove", winMove )
        .on( onDesktop ? "mouseup" : "touchend", winRelease )
    ;
    
    $.element({
        name: "joystick",
        html: "<div></div>",
        css: "\
            .joystick {\
                display: inline-block;\
                position: relative;\
                width: 100px;\
                height: 100px;\
                border: 1px solid;\
                border-radius: 50%;\
                transition: opacity 1s ease;\
                opacity: .3;\
                cursor: move;\
            }\
            .joystick,\
            .joystick * {\
                box-sizing: border-box;\
            }\
            .joystick.joystick-show {\
                transition-duration: .2s;\
                opacity: 1;\
            }\
            .joystick:before,\
            .joystick * {\
                position: absolute;\
                width: 50%;\
                height: 50%;\
                left: 25%;\
                top: 25%;\
                border-radius: 50%;\
            }\
            .joystick:before {\
                content: '';\
                box-sizing: content-box;\
                margin: -7px;\
                border: 2px dashed;\
                padding: 5px;\
                opacity: .5;\
            }\
            .joystick * {\
                border: 2px solid;\
                background-position: center;\
                transition-property: border-width;\
                transition-duration: inherit;\
                transition-timing-function: inherit;\
            }\
            .joystick.joystick-show * {\
                border-width: 5px;\
            }\
            .joystick.joystick-reset * {\
                transition-property: border-width, margin;\
                transition-duration: .1s;\
            }\
        ",
        init: function() {
    
            // First, initialize all the user's callback.
            this.init({});
    
            // This is the bouton inside the joystick himself.
            // this.jqElement IS the joystick himself (the container).
            this.jqBtn =
                this.jqElement
                    .addClass( "joystick" )
                    .children()
                ;
    
            // Attributes.
            this.radius = this.jqElement.width() / 2;
            this.isHolding = false;
            this.identifier;
            this.coordX;
            this.coordY;
            this.btnCoordX =
            this.btnCoordY = 0;
    
            var that = this;
    
            this.jqElement
                .on( onDesktop ? "mousedown" : "touchstart", function( e ) {
                    var t, i = 0, pos = e;
                    if ( onDesktop ) {
                        joystickCurrent = that;
                    } else {
                        e = e.originalEvent;
                        while ( t = e.changedTouches[ i++ ] ) {
                            if ( t.target === that.jqElement[ 0 ] || t.target === that.jqBtn[ 0 ] ) {
                                break;
                            }
                        }
                        if ( !t ) {
                            return;
                        }
                        pos = t;
                        that.identifier = t.identifier;
                        joystickCurrent = joystickCurrent || [];
                        joystickCurrent[ t.identifier ] = that;
                    }
                    e.preventDefault();
                    that.click(
                        pos.pageX,
                        pos.pageY
                    );
                })
            ;
        },
        
        prototype: {
    
            // public:
            init: function( p ) {
                // User's callbacks.
                this.cbMove    = p.move    || $.noop;
                this.cbHold    = p.hold    || $.noop;
                this.cbRelease = p.release || $.noop;
            },
    
            // private:
            click: function( x, y ) {
                this.isHolding = true;
                this.btnCoordX =
                this.btnCoordY = 0;
                this.coordX = x;
                this.coordY = y;
                this.jqElement
                    .removeClass( "joystick-reset" )
                    .addClass( "joystick-show" )
                ;
                this.cbHold.call( this.jqElement[ 0 ] );
            },
            moveBtn: function( x, y, rx, ry ) {
                this.jqBtn.css({
                    marginLeft: x,
                    marginTop: y,
                });
                this.cbMove.call(
                    this.jqElement[ 0 ],
                    x / this.radius,
                    y / this.radius,
                    rx, ry
                );
                cam_request("cammove",x, y);
            },
            move: function( x, y ) {
                var a, d, rx, ry;
                rx = x - this.coordX;
                ry = y - this.coordY;
                this.coordX = x;
                this.coordY = y;
                x = this.btnCoordX += rx;
                y = this.btnCoordY += ry;
                d = Math.min( Math.sqrt( x * x + y * y ), this.radius );
                a = Math.atan2( y, x );
                this.moveBtn(
                    Math.cos( a ) * d,
                    Math.sin( a ) * d,
                    rx, ry
                );
            },
            release: function() {
                this.isHolding = false;
                this.jqElement
                    .removeClass( "joystick-show" )
                    .addClass( "joystick-reset" )
                ;
                this.moveBtn(
                    0, 0,
                    -this.btnCoordX,
                    -this.btnCoordY
                );
            }
        }
    })
    $.element({
        name: "joystick2",
        html: "<div></div>",
        css: "\
            .joystick2 {\
                display: inline-block;\
                position: relative;\
                width: 100px;\
                height: 100px;\
                border: 1px solid;\
                border-radius: 50%;\
                transition: opacity 1s ease;\
                opacity: .3;\
                cursor: move;\
            }\
            .joystick2,\
            .joystick2 * {\
                box-sizing: border-box;\
            }\
            .joystick2.joystick2-show {\
                transition-duration: .2s;\
                opacity: 1;\
            }\
            .joystick2:before,\
            .joystick2 * {\
                position: absolute;\
                width: 50%;\
                height: 50%;\
                left: 25%;\
                top: 25%;\
                border-radius: 50%;\
            }\
            .joystick2:before {\
                content: '';\
                box-sizing: content-box;\
                margin: -7px;\
                border: 2px dashed;\
                padding: 5px;\
                opacity: .5;\
            }\
            .joystick2 * {\
                border: 2px solid;\
                background-position: center;\
                transition-property: border-width;\
                transition-duration: inherit;\
                transition-timing-function: inherit;\
            }\
            .joystick2.joystick2-show * {\
                border-width: 5px;\
            }\
            .joystick2.joystick2-reset * {\
                transition-property: border-width, margin;\
                transition-duration: .1s;\
            }\
        ",
        init: function() {
    
            // First, initialize all the user's callback.
            this.init({});
    
            // This is the bouton inside the joystick himself.
            // this.jqElement IS the joystick himself (the container).
            this.jqBtn =
                this.jqElement
                    .addClass( "joystick2" )
                    .children()
                ;
    
            // Attributes.
            this.radius = this.jqElement.width() / 2;
            this.isHolding = false;
            this.identifier;
            this.coordX;
            this.coordY;
            this.btnCoordX =
            this.btnCoordY = 0;
    
            var that = this;
    
            this.jqElement
                .on( onDesktop ? "mousedown" : "touchstart", function( e ) {
                    var t, i = 0, pos = e;
                    if ( onDesktop ) {
                        joystickCurrent = that;
                    } else {
                        e = e.originalEvent;
                        while ( t = e.changedTouches[ i++ ] ) {
                            if ( t.target === that.jqElement[ 0 ] || t.target === that.jqBtn[ 0 ] ) {
                                break;
                            }
                        }
                        if ( !t ) {
                            return;
                        }
                        pos = t;
                        that.identifier = t.identifier;
                        joystickCurrent = joystickCurrent || [];
                        joystickCurrent[ t.identifier ] = that;
                    }
                    e.preventDefault();
                    that.click(
                        pos.pageX,
                        pos.pageY
                    );
                })
            ;
        },
        
        prototype: {
    
            // public:
            init: function( p ) {
                // User's callbacks.
                this.cbMove    = p.move    || $.noop;
                this.cbHold    = p.hold    || $.noop;
                this.cbRelease = p.release || $.noop;
            },
    
            // private:
            click: function( x, y ) {
                this.isHolding = true;
                this.btnCoordX =
                this.btnCoordY = 0;
                this.coordX = x;
                this.coordY = y;
                this.jqElement
                    .removeClass( "joystick2-reset" )
                    .addClass( "joystick2-show" )
                ;
                this.cbHold.call( this.jqElement[ 0 ] );
            },
            moveBtn: function( x, y, rx, ry ) {
                this.jqBtn.css({
                    marginLeft: x,
                    marginTop: y,
                });
                this.cbMove.call(
                    this.jqElement[ 0 ],
                    x / this.radius,
                    y / this.radius,
                    rx, ry
                );
                request("dronemove",x, y);
            },
            move: function( x, y ) {
                var a, d, rx, ry;
                rx = x - this.coordX;
                ry = y - this.coordY;
                this.coordX = x;
                this.coordY = y;
                x = this.btnCoordX += rx;
                y = this.btnCoordY += ry;
                d = Math.min( Math.sqrt( x * x + y * y ), this.radius );
                a = Math.atan2( y, x );
                this.moveBtn(
                    Math.cos( a ) * d,
                    Math.sin( a ) * d,
                    rx, ry
                );
                //request("dronemove",x, y);
            },
            release: function() {
                this.isHolding = false;
                this.jqElement
                    .removeClass( "joystick2-show" )
                    .addClass( "joystick2-reset" )
                ;
                this.moveBtn(
                    0, 0,
                    -this.btnCoordX,
                    -this.btnCoordY
                );
            }
        }
    });
    })( jQuery );
