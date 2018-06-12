var addToCal = {
    buildDate: function(dateFrom, dateTo) {
        var momentDateFrom
        var momentDateTo

        if (dateFrom != '' && dateTo != '') {
            momentDateTo = moment(dateTo)
        } else {
            momentDateTo = moment(dateFrom)
        }
        momentDateFrom = moment(dateFrom)
        momentDateTo = momentDateTo.add(1, 'days')
        console.log(moment(momentDateFrom).format("YYYYMMDD") + '/' + moment(momentDateTo).format("YYYYMMDD"))

        return moment(momentDateFrom).format("YYYYMMDD") + '/' + moment(momentDateTo).format("YYYYMMDD")
    },

    buildDateTime: function(dateFrom, timeFrom , dateTo, timeTo) {
        var momentFrom = moment(dateFrom + " " + timeFrom)
        var momentTo = moment(dateTo + " " + timeTo)

        return moment(momentFrom).format('YYYYMMDDTHHmmss') + '/' + moment(momentTo).format('YYYYMMDDTHHmmss')
    },

    buildUrl: function(title, details, location, dates) {
        var url = 'https://calendar.google.com/calendar/r/eventedit'
        url += '?text=' + title
        url += '&details=' + details
        url += '&location=' + location
        url += '&dates=' + dates

        return url
    },

    openWindow: function(url) {
        var googleWindow = window.open(url, '_blank');
        googleWindow.location;
    }
}


$('.js-addToCal').on('click', function(event) {
    event.stopPropagation();

    var dataObject = $(this).data();
    var dates;
    var url;

    if ((dataObject.timeFrom != '' && !!dataObject.timeFrom) && (dataObject.timeTo != '' && !!dataObject.timeTo)) {
        console.log(dataObject.timeTo)
        dates = addToCal.buildDateTime(dataObject.dateFrom, dataObject.timeFrom, dataObject.dateTo, dataObject.timeTo);
        console.log(dates)
    } else {
        dates = addToCal.buildDate(dataObject.dateFrom, dataObject.dateTo);
    }

    url = addToCal.buildUrl(dataObject.title, dataObject.url, dataObject.location, dates);

    addToCal.openWindow(url);

    return false;
})