$('.calendar__item--tile').each(function() {
    $(this).qtip({
        content: $(this).next(),
        position: {
            my: 'top center',  // Position my top left...
            at: 'bottom center', // at the bottom right of...
        },
        hide: {
            fixed: true,
            delay: 300
        },
        style: { classes: 'calendar__dropdown' }
    })
})

var mobileWindow = 480;

var calendar = {
    init: function() {
        this.setToday()
    },

    setToday: function() {
        var todayOffset = $('.calendar__item.is-today').offset().left
        var containerOffset = $('.calendar__items').offset().left
        var boxWidth = $('.calendar__item.is-today').outerWidth(true)
        var boxesBeforeToday = ($(window).width() > mobileWindow) ? 3 : 1
        var boxPos = - (todayOffset - containerOffset - (boxesBeforeToday * boxWidth))
        
        this._setPosition(boxPos)
    },

    next: function() {
        var newPosition = this._getPosition() - this._boxWidthSlide()

        if (newPosition > this._containerWidth()){
            this._setPosition(newPosition)
        } else {
            this._setPosition(this._containerWidth())
            $('.calendar__button--next').attr('disabled', true)
        }

        this._checkButton('prev');
        this._checkButton('next');

    },

    prev: function() {
        var newPosition = this._getPosition() + this._boxWidthSlide()

        if (newPosition < 0) {
            this._setPosition(newPosition)
        } else {
            this._setPosition(0)
        }

        this._checkButton('prev');
        this._checkButton('next');

    },

    _getPosition: function() {
        return parseInt($('.calendar__items').css('left').replace(/[^-\d\.]/g, ''))
    },

    _setPosition: function(leftPosition) {
        return $('.calendar__items').css('left', leftPosition + 'px')
    },

    _containerWidth: function() {
        return - ($('.calendar__items').get(0).scrollWidth - $('.calendar__items').width())
    },

    _boxWidthSlide: function() {

        if ($(window).width() > mobileWindow) {
            return parseInt($('.calendar__item.is-today').width()) * 3
        } else {
            return parseInt($('.calendar__item.is-today').width())
        }

    },

    _checkButton: function(button) {
        var position = (button == 'prev') ? 0 : this._containerWidth();

        if (this._getPosition() == position) {
            $('.calendar__button--' + button).attr('disabled', true)
        } else {
            if (!(!$('.calendar__button--' + button).attr('disabled'))) {
                $('.calendar__button--' + button).attr('disabled', false)
            }
        }
    }
}

if ($('.calendar').length > 0) {
    calendar.init()
}

$('.calendar__button--next').on('click', function(){
    calendar.next()
})

$('.calendar__button--prev').on('click', function(){
    calendar.prev()
})