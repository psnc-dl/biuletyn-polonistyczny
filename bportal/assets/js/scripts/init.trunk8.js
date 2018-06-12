$.fn.extend(
    {
        truncateTextNote: function () {
            var that = this;
            return this.each(function() {
                $(this).trunk8({
                    fill: '(...)<i class="bp-icon-more_text"></i>',
                    splitOn: ' ',
                    onTruncate: function () {
                        $(that).qtip({
                            position: {
                                viewport: $(window),
                                adjust: {
                                    x: 10,
                                    y: 10
                                },
                                target: 'mouse'
                            }
                        })
                    }
                });
            });
        },

        truncateTextNoteTwo: function () {
            var that = this;
            return this.each(function() {
                $(this).trunk8({
                    fill: '(...)<i class="bp-icon-more_text"></i>',
                    splitOn: ' ',
                    lines: 2,

                    onTruncate: function () {
                        $(that).qtip({
                            position: {
                                viewport: $(window),
                                adjust: {
                                    x: 10,
                                    y: 10
                                },
                                target: 'mouse'
                            }
                        })
                    }
                });
            });
        },

        truncateTextOne: function () {
            var that = this;
            return this.each(function() {
                $(this).trunk8({
                    fill: '(...)',
                    splitOn: ' ',
                });
            });
        },

        truncateTextTwo: function () {
            var that = this;
            return this.each(function() {
                $(this).trunk8({
                    fill: '(...)',
                    splitOn: ' ',
                    lines: 2,
                });
            });
        },

        truncateTextThree: function () {
            return this.each(function() {
                $(this).trunk8({
                    fill: '(...)',
                    splitOn: ' ',
                    lines: 3,
                });
            });
        },

        truncateTextFive: function () {
            return this.each(function() {
                $(this).trunk8({
                    fill: '(...)',
                    splitOn: ' ',
                    lines: 5,
                });
            });
        }
    });

$(".js-truncate").truncateTextNote();
$(".js-truncate-note-two").truncateTextNoteTwo();
$(".js-truncate-one").truncateTextOne();
$(".js-truncate-two").truncateTextTwo();
$(".js-truncate-three").truncateTextThree();
$(".js-truncate-five").truncateTextFive();
