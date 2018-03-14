var imageId = [];
var index = 0;

$(document).ready(function() {
    $('.next').on('click', nextImage);
    $('.prev').on('click', prevImage);

    $(window).on('load', function() {
        var url = '/doc/all';
        $.get(url).done(function(data) {
            $('#image').on('load', function() {
                $('.view-panel').css('height', $(this).css('height'));
                $(this).css('display', 'block');
            });

            imageId = data;
            loadImage();
        });
    });
});

function nextImage() {
    index += 1;
    if (index >= imageId.length) {
        index -= imageId.length;
    }

    loadImage();
}

function prevImage() {
    index -= 1;
    if (index < 0) {
        index += imageId.length;
    }

    loadImage();
}

function loadImage() {
    $('.image').css('display', 'none');

    var url = '/image/guest?id=' + imageId[index];
    $('#image').attr('src', url);
}