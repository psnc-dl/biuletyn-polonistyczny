var baseURL = null;
if (baseURL == undefined) {
    var url = window.location.href;
    if (window.location.search) {
        url = url.substring(0, url.indexOf('?'));
    }
    $.ajax({
        url: url.indexOf("/", url.length - 1) ? url + "base_url/" : url + "/base_url/",
        dataType: 'json',
        async: false,
        data: {},
        success: function(data) {
            baseURL = data.base_url;
        }
    });
}
