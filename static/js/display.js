var maxImageId = 19;
var defaultImageId = 1;
var previousTimestamp = 0;

$(document).ready(function() {
    $(window).on('load', function() {
        setTimeout(initDisplay, 4000);
    });
});

function initDisplay() {
    $('.slide-image').each(function() {
        $(this).on('load', function() {
            console.log('Received image');
            $('.slide-text').fadeOut(1500, function() {
                setSlideText();
                showSlideText();
            });
            $('.active').fadeOut(3000, function() {
                $(this).removeClass('active').addClass('inactive');
            });
            $('.inactive').fadeIn(3000, function() {
                $(this).removeClass('inactive').addClass('active');
            });
        });
    });

    $('.splash-container').fadeOut(1250);
    $('.main-container').fadeIn(3000, function() {
        setTimeout(changeSlide, 8000);
    });
    $('.url-container').fadeIn(3000);

    $('.splash-content').animate(
        {top: '75%'}, 2000, function() {
            $('.splash-container').remove();
        }
    );
}

function setSlideText(category, caption) {
    console.log('Setting slide text');
    var category = $('#category-value').val();
    var caption= $('#caption-value').val();
    $('.category').html(category);
    $('.caption').html(caption);
}

function showSlideText() {
    var category = $('#category-value').val();
    var caption= $('#caption-value').val();
    if (category.length > 1 || caption.length > 0) {
        if (category.length <= 1 || caption.length <= 0) {
            $('.spacer').css('display', 'block');
        } else {
            $('.spacer').css('display', 'none');
        }

        $('.slide-text').fadeIn(1500);
    }
}

function changeSlide() {
    var activeImage = $('.active');
    var inactiveImage = $('.inactive');

    var categoryInput = $('#category-value');
    var captionInput = $('#caption-value');

    var url = '/doc/recent?time=' + previousTimestamp;
    $.get(url).done(function(data) {
        console.log('Received document');
        console.log('Document Content: ' + data);
        var src;
        var category;
        var caption;

        if (data != undefined && data['id'] != undefined) {
            console.log('Document contains image data');
            src = '/image/guest?id=' + data['id'];
            if (data['category'].length > 0) {
                category = '#' + data['category'];
            } else {
                category = '';
            }
            caption = data['caption'];
            previousTimestamp = data['timestamp'];
        } else {
            console.log('Document is empty');
            src = '/image/host?id=' + defaultImageId;
            category = '#Wedding';
            caption = 'Steven & Nikki Stanley';
            defaultImageId = (defaultImageId + 1) % maxImageId;
        }

        categoryInput.val(category);
        captionInput.val(caption);
        inactiveImage.attr('src', src);

        console.log('Image source set as ' + src);

        setTimeout(changeSlide, 10000);
    });
}
