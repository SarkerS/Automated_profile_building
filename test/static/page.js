function getParameterByName(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

function listify_obj(obj) {
    var list = '<ul>';
    for (var property in obj) {
        item = obj[property];
        
        if (typeof item === 'object') {
            if (property === 'links') {
                for (var i in item) {
                    list += '<li>';
                    list += '<a href="' + item[i] + '">' + item[i] + '</a>';
                    list += '</li>';
                }
            }
            else {
                list += '<li>';
                var isArray = /^\d+$/.test(property);
                if (isArray) {
                    list += 'Item ' + (parseInt(property) + 1) + ':';
                }
                else {
                    list += property + ':';
                }
                list += listify_obj(item);
                list += '</li>';
            }
        }
        else {
            list += '<li>';
            list += property + ': ' + item;
            list += '</li>';
        }
    }
    list += '</ul>';

    return list;
}

function populate_results(resp) {
    people = JSON.parse(resp);
    var results_div = $('#results');
    results_div.empty();
    $.each(people, function(i, person) {
        
        var div = '<div class="profileDiv centerBig">'
        div += '<a href="' + person['url'] + '">';
        div += '<img src="' + person['pic_url'] + '" class="profilePic"/>';
        div += '</a>';
        
        div += '<p>Name: <a href="' + person['url'] + '">' + person['name'] + '</a></p>';

        if ('other' in person) {
            div += listify_obj(person['other']);
        }
        
        div += '</div>';
        
        results_div.append(div);
    })
}

function search() {
    name = $('#searchBox')[0].value
    if (name == '')
    {
        return;
    }

    var results_div = $('#results');
    results_div.append('<img src="/static/ajax-loader.gif" class="loader">')
    
    $.ajax({
        url: '/search',
        data: {
            query: name
        },
        type: 'GET',
        
    })
        .done(populate_results);
}

$(document).ready(function() {
    $('#searchButton').button();
    $('#searchBox').addClass("ui-widget ui-widget-content ui-corner-all ui-button gfont");
    $('#searchBox').focus();
    //$('#searchBox').val('John Smith');
});
