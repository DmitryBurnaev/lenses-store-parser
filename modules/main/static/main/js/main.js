/**
 * Created by dmitry on 16.07.16.
 */

function StartEndCheckParsing(){

    this.init = function(){
        this.bindEvents();
        if ($('#start-button-id').data('parseInProgress')){
            this.checkResult();
        }
    };

    this.bindEvents = function () {
        var _this = this;
        $('#start-button-id').click(function(){
             _this.startParsing()
        })

    };

    this.startParsing = function(){
        var _this = this;
        $.ajax('/parsing/start/')
            .done(function(result) {
                console.log(result.message);
                _this.checkResult()
            })
            .fail(function(result) {
                alert( "error" );
            })
    };

    this.checkResult = function(){
        var _this = this;
        $('#start-button-id').attr('disabled', true);
        $('#throbber').css('visibility', 'visible');
        setTimeout(function () {
            _this.intervalId = setInterval(function(){
                $.ajax('/parsing/check/').done(function(result) {
                        console.log(result.message);
                    if (result.data.status == 'READY'){
                        clearInterval(_this.intervalId);
                        _this.applyResult()
                    }
                })
            }, 2000)
        }, 2000)


    };

    this.applyResult = function(){
        location.reload()
    };

}


$(document).ready(function(){
    var parsing = new StartEndCheckParsing();
    parsing.init();

});